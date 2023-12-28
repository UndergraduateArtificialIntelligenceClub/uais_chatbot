from api.google_calendar_api import GoogleCalendarAPI
from views.event_creation_view import EventCreationView
from discord.ext import commands


class Calendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.google_calendar = GoogleCalendarAPI()

    @commands.command(brief='Lists 10 (or specified number of) upcoming Google Calendar events', aliases=['calendar', 'ev'])
    async def events(self, ctx, events_num=10):
        if (not isinstance(events_num, int)) or (events_num < 1) or (events_num > 30):
            await ctx.send(content="Invalid number of events provided. Must be int and in [1, 30]")
            return

        await ctx.send(content=self.google_calendar.list_events(events_num))

    @commands.command(brief='Opens event creation menu', aliases=['pl'])
    @commands.has_permissions(administrator=True)
    async def plan(self, ctx):
        # Send the event creation menu (view)
        event_creation_view = EventCreationView(user=ctx.author)
        await ctx.send(content="**Event creation menu:**", view=event_creation_view)
        # Wait until it finishes execution
        await event_creation_view.wait()

        # Get event data
        event = event_creation_view.eventinfo
        if event:
            payload = f"{event[0]},{event[1]},{event[2]},{event[3]},{event[4]}"
            await ctx.send(content=self.google_calendar.create_event(payload))

    @commands.command(brief='Plans an event from one text command call. Call without arguments to see format', aliases=['plc', 'planc', 'plcli'])
    @commands.has_permissions(administrator=True)
    async def plancli(self, ctx, *, payload=""):
        if not payload:
            await ctx.send(content="!plancli Summary,Location,Description,Start time,End time\ne.g.\n!plancli Test event,University of Alberta,Description,2023-12-20T09:00:00,2023-12-21T17:00:00")
            return

        await ctx.send(content=self.google_calendar.create_event(payload))


async def setup(bot):
    await bot.add_cog(Calendar(bot))
