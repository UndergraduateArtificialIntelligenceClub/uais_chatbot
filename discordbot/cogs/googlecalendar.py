import os
import json
import pytz
import discord
from api.google_calendar_api import GoogleCalendarAPI
from views.event_creation_view import EventCreationView
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
TIMEZONE = os.environ['TIMEZONE']


class Calendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.google_calendar = GoogleCalendarAPI()
        self.active_menus = set()
        # Set this via a command
        self.reminder_channel = None
        self.guild = None
        # Default time before event to send reminder
        self.reminder_time_before = timedelta(hours=5)
        self.reminded_events = set()
        self.event_reminders.start()

    def get_event_mentions(self, event):
        # Get roles, if available (stored in tags property)
        roles_json = event.get('extendedProperties', {}).get('private', {}).get('tags', '')
        roles = json.loads(roles_json) if roles_json else []

        roles_mention = " ".join([f"{role.mention}" for role_name in roles if (
            role := discord.utils.get(self.guild.roles, name=role_name.strip())) is not None])

        return roles_mention

    def get_reminder_embed(self, event, start_dt):
        summary = event.get('summary')
        description = event.get('description')
        location = event.get('location')

        start_formatted = start_dt.strftime(
            "%B %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

        embed = discord.Embed(
            title=f"Reminder:\n**{summary}** is starting soon!", color=discord.Color.random())

        embed.add_field(name="Start time:", value=f"**{start_formatted}**", inline=False)

        if description:
            embed.add_field(name="Description:", value=description, inline=False)
        if location:
            embed.add_field(name="Location:", value=location, inline=False)

        return embed

    @tasks.loop(seconds=10)
    async def event_reminders(self):
        if self.reminder_channel is None:
            return

        upcoming_events = self.google_calendar.get_events(10)
        if not upcoming_events:
            return

        now = datetime.now(pytz.timezone(TIMEZONE))

        for event in upcoming_events:
            start_iso = event["start"].get(
                "dateTime", event["start"].get("date"))
            start = datetime.fromisoformat(start_iso)
            id = event.get("id")

            if id not in self.reminded_events and now + self.reminder_time_before >= start:
                self.reminded_events.add(id)
                await self.reminder_channel.send(content=self.get_event_mentions(event), embed=self.get_reminder_embed(event, start))

    @event_reminders.before_loop
    async def before_event_reminders(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setreminderchannel(self, ctx, channel_id: int):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Cannot get_channel with provided channel id.")
            return

        self.reminder_channel = channel
        self.guild = ctx.guild
        await ctx.send(f"Reminder channel set to <#{channel_id}>.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setremindertime(self, ctx, hours_before: int):
        
        if (hours_before < 1):
            await ctx.send("Invalid reminder time.")
            return

        self.reminder_time_before = timedelta(hours=hours_before)
        await ctx.send(f"Reminders will be sent {hours_before} hours before events.")

    @commands.command(brief='Opens event creation menu', aliases=['pl'])
    @commands.has_permissions(administrator=True)
    async def plan(self, ctx):
        # Check if the user already has an active menu
        if ctx.author.id in self.active_menus:
            await ctx.send("You already have an active event creation menu.")
            return

        # Send the event creation menu (view)
        event_creation_view = EventCreationView(user=ctx.author)
        msg = await ctx.send(content="**Event creation menu:**", view=event_creation_view)

        # Add the user to the set of active menus
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

        response = self.google_calendar.create_event(event_data.get("summary"), event_data.get("location"),
                                                     event_data.get("description"), event_data.get("start_time"), event_data.get("end_time"), tags=roles_to_remind)

        await ctx.send(content=response)

    @commands.command(brief='Plans an event from one text command call. Call without arguments to see format', aliases=['plc', 'planc', 'plcli'])
    @commands.has_permissions(administrator=True)
    async def plancli(self, ctx, *, payload=""):
        if not payload:
            line_1 = r'!plancli Summary;Location;Description;Start time: %d/%m/%Y %H:%M:%S;End time: %d/%m/%Y %H:%M:%S;role1, role2, ...'
            line_2 = '!plancli Test event;University of Alberta;Description;20/11/2024 09:15:30;20/11/2024 10:00:00; role1, role2'

            await ctx.send(content=line_1+"\ne.g.\n"+line_2)
            return

        argument_list = payload.split(';')

        if (len(argument_list) != 5) and (len(argument_list) != 6):
            await ctx.send(content="Invalid number of arguments. Call !plancli without arguments to see proper format example")
            return

        tags = argument_list[5].strip().split(',') if len(argument_list) > 5 else None

        try:
            start_time = datetime.strptime(argument_list[3], "%d/%m/%Y %H:%M:%S")
            end_time = datetime.strptime(argument_list[4], "%d/%m/%Y %H:%M:%S")
        except ValueError:
            await ctx.send(content="Could not convert start_time or end_time to datetime object")
            return

        response = self.google_calendar.create_event(argument_list[0], argument_list[1], argument_list[2], start_time, end_time, tags)

        await ctx.send(content=response)

    @commands.command(brief='Lists 10 (or specified number of) upcoming Google Calendar events', aliases=['calendar', 'ev'])
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
            formatted_start = start_dt.strftime(
                "%B %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

            output += f"**{formatted_start}:** {event['summary']}\n"

        await ctx.send(content=output)


async def setup(bot):
    await bot.add_cog(Calendar(bot))
