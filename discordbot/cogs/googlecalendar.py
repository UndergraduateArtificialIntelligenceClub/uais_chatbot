from api.google_calendar_api import GoogleCalendarAPI
from views.event_creation_view import EventCreationView
from discord.ext import commands
from datetime import datetime


class Calendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.google_calendar = GoogleCalendarAPI()
        self.active_menus = set()

    @commands.command(brief='Lists 10 (or specified number of) upcoming Google Calendar events', aliases=['calendar', 'ev'])
    async def events(self, ctx, events_num=10):
        if (not isinstance(events_num, int)) or (events_num < 1) or (events_num > 30):
            await ctx.send(content="Invalid number of events provided. Must be int and in [1, 30]")
            return

        await ctx.send(content=self.google_calendar.list_events(events_num))

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
        response = self.google_calendar.create_event(event_data.get("summary"), event_data.get("location"),
                                                     event_data.get("description"), event_data.get("start_time"), event_data.get("end_time"), tags=event_data.get("tags"))

        await ctx.send(content=response)

    @commands.command(brief='Plans an event from one text command call. Call without arguments to see format', aliases=['plc', 'planc', 'plcli'])
    @commands.has_permissions(administrator=True)
    async def plancli(self, ctx, *, payload=""):
        if not payload:
            line_1 = r'!plancli Summary;Location;Description;Start time: %d/%m/%Y %H:%M:%S;End time: %d/%m/%Y %H:%M:%S;tag1, tag2, ...'
            line_2 = '!plancli Test event;University of Alberta;Description;12/11/2024 09:15:30;12/11/2024 10:00:00; tag1, tag2'

            await ctx.send(content=line_1+"\n"+line_2)
            return

        argument_list = payload.split(';')

        if (len(argument_list) != 5) and (len(argument_list) != 6):
            await ctx.send(content="Invalid number of arguments. Call !plancli without arguments to see proper format example")
            return

        if len(argument_list) == 5:
            tags = None
        else:
            tags = argument_list[5].strip().split(',')

        try:
            start_time = datetime.strptime(
                argument_list[3], "%d/%m/%Y %H:%M:%S")
            end_time = datetime.strptime(argument_list[4], "%d/%m/%Y %H:%M:%S")
        except ValueError:
            await ctx.send(content="Could not convert start_time or end_time to datetime object")

        try:
            response = self.google_calendar.create_event(
                argument_list[0], argument_list[1], argument_list[2], start_time, end_time, tags)
        except Exception as e:
            print(e)

        await ctx.send(content=response)


async def setup(bot):
    await bot.add_cog(Calendar(bot))
