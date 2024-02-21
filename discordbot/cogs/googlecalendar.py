import json
import os
import logging
import discord
from datetime import datetime, timedelta
from discord.ext import commands, tasks
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from api.google_calendar_api import GoogleCalendarAPI
from views.event_creation_view import EventCreationView

load_dotenv()
TIMEZONE = os.environ['TIMEZONE']


def get_event_mentions(event, guild: discord.Guild):
    roles_json = event.get('extendedProperties', {}).get('private', {}).get('roles', '')
    roles = json.loads(roles_json) if roles_json else None

    if roles is None:
        return ""

    roles_mention = " ".join([f"{role.mention}" for role_name in roles if (
        role := discord.utils.get(guild.roles, name=role_name.strip())) is not None])

    return roles_mention


def get_reminder_embed(event, start_dt: datetime):
    summary = event.get('summary')
    description = event.get('description')
    location = event.get('location')

    start_formatted = start_dt.strftime("%B %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

    now = datetime.now(start_dt.tzinfo)
    time_diff = start_dt - now

    hrs_left = int(time_diff.total_seconds() / 3600)
    hours = f"hour{'s' if hrs_left != 1 else ''}"

    mins_left = int(time_diff.total_seconds() / 60) - (hrs_left * 60)
    minutes = f"minute{'s' if mins_left != 1 else ''}"

    if hrs_left == 0:
        title = f"Reminder:\n**{summary}** starts in **{mins_left}** {minutes}!"
    elif mins_left == 0:
        title = f"Reminder:\n**{summary}** starts in **{hrs_left}** {hours}!"
    else:
        title = f"Reminder:\n**{summary}** starts in **{hrs_left}** {hours} **{mins_left}** {minutes}!"

    embed = discord.Embed(title=title, color=discord.Color.random())

    embed.add_field(name="Start time:",value=f"**{start_formatted}**", inline=False)

    if description:
        embed.add_field(name="Description:", value=description, inline=False)
    if location:
        embed.add_field(name="Location:", value=location, inline=False)

    return embed


class Calendar(commands.Cog):

    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot
        self.google_calendar = GoogleCalendarAPI()
        self.active_menus = set()
        self.scheduled_events = set()
        self.reminder_channel_id = None
        self.default_reminders_mins = [1440, 180, 15]
        self.settings_file = 'reminderchannel.json'
        self.load_settings()
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        self.schedule_reminders.start()

    def cog_unload(self):
        self.scheduler.shutdown(wait=False)
        self.schedule_reminders.cancel()

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.reminder_channel_id = settings.get('reminder_channel_id')
                default_reminders_mins_json = settings.get('default_reminders_mins')
                self.default_reminders_mins = json.loads(default_reminders_mins_json)
        except FileNotFoundError:
            self.save_settings()  # Create the file if it doesn't exist

    def save_settings(self):
        settings = {
            'reminder_channel_id': self.reminder_channel_id,
            'default_reminders_mins': json.dumps(self.default_reminders_mins)
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    def schedule_event_reminder(self, event):
        start_iso = event["start"].get("dateTime", event["start"].get("date"))
        start = datetime.fromisoformat(start_iso)

        minute_offsets_json = event.get('extendedProperties', {}).get('private', {}).get('reminderMinutes', '')
        minute_offsets = json.loads(minute_offsets_json) if minute_offsets_json else self.default_reminders_mins

        for minute_offset in minute_offsets:
            reminder_time = start - timedelta(minutes=minute_offset)
            self.scheduler.add_job(self.send_reminder, 'date', run_date=reminder_time, args=[
                                   event, start], misfire_grace_time=300)

    async def send_reminder(self, event, start):
        reminder_channel = self.bot.get_channel(self.reminder_channel_id)
        if reminder_channel is None:
            logging.error(f'Failed to send reminder for event {event.get("id")} - the reminder channel could not be accessed')
            return

        await reminder_channel.send(content=get_event_mentions(event, reminder_channel.guild), embed=get_reminder_embed(event, start))

    @tasks.loop(hours=1)
    async def schedule_reminders(self):
        custom_reminders = self.google_calendar.get_events(max_results=None, custom_reminders=True)
        default_reminders = self.google_calendar.get_events(max_results=15)

        for event in custom_reminders + default_reminders:
            event_id = event.get('id')
            if event_id not in self.scheduled_events:
                self.schedule_event_reminder(event)
                self.scheduled_events.add(event_id)

    @schedule_reminders.before_loop
    async def before_schedule_reminders(self):
        await self.bot.wait_until_ready()

    @commands.command(brief='Call with 1 argument: channel id')
    @commands.has_permissions(administrator=True)
    async def setreminderchannel(self, ctx, channel_id: int):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Cannot access channel with provided channel id.")
            return

        self.reminder_channel_id = channel_id
        self.save_settings()
        await ctx.send(f"Reminder channel is now <#{channel_id}>. Saved to a json file for persistency.")

    @commands.command(brief='Opens event creation menu', aliases=['pl'])
    @commands.has_permissions(administrator=True)
    async def plan(self, ctx):
        if ctx.author.id in self.active_menus:
            await ctx.send("You already have an active event creation menu.")
            return

        # Send the event creation menu (view)
        event_creation_view = EventCreationView(user=ctx.author)
        msg = await ctx.send(content="**Event creation menu:**", view=event_creation_view)

        self.active_menus.add(ctx.author.id)

        # Wait until it finishes execution and notify user if it times out
        if await event_creation_view.wait():
            await msg.edit(content="Event creation menu timed out.", view=None)
            self.active_menus.discard(ctx.author.id)
            return

        self.active_menus.discard(ctx.author.id)

        # Get event data
        event_data = event_creation_view.event_data
        roles_to_remind = event_creation_view.selected_roles
        offsets = event_creation_view.minute_offsets

        response = self.google_calendar.create_event(event_data.get("summary"), event_data.get("location"),
                                                     event_data.get("description"), event_data.get("start_time"),
                                                     event_data.get("end_time"), roles=roles_to_remind, mins_before_reminder=offsets)

        await ctx.send(content=response)

    @commands.command(brief='Lists 10 (or specified number of) upcoming events', aliases=['calendar', 'ev'])
    async def events(self, ctx, events_num=10):
        if (events_num < 1) or (events_num > 30):
            await ctx.send(content="Invalid number of events provided. Must be int and in [1, 30]")
            return

        upcoming_events = self.google_calendar.get_events(events_num)
        if not upcoming_events:
            await ctx.send(content="No upcoming events found.")
            return

        output = ""
        for event in upcoming_events:
            # Get event start time
            start = event["start"].get("dateTime", event["start"].get("date"))

            # Convert to human readable format
            start_dt = datetime.fromisoformat(start)
            formatted_start = start_dt.strftime("%B %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

            output += f"**{formatted_start}:** {event['summary']}\n"

        await ctx.send(content=output)


async def setup(bot):
    await bot.add_cog(Calendar(bot))
