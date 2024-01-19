from api.google_calendar_api import GoogleCalendarAPI
from views.event_creation_view import EventCreationView
from discord.ext import commands


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
        event_list = [event_data.get("summary"), event_data.get("location"),
                      event_data.get("description"), event_data.get("start_time"), event_data.get("end_time")]

        payload = ",".join(event_list)
        await ctx.send(content=self.google_calendar.create_event(payload))

    @commands.command(brief='Plans an event from one text command call. Call without arguments to see format', aliases=['plc', 'planc', 'plcli'])
    @commands.has_permissions(administrator=True)
    async def plancli(self, ctx, *, payload=""):
        if not payload:
            await ctx.send(content="!plancli Summary,Location,Description,Start time,End time\ne.g.\n!plancli Test event,University of Alberta,Description,2023-12-20T09:00:00,2023-12-21T17:00:00")
            return

        response = self.google_calendar.create_event(payload)

        if not response:
            await ctx.send(content="Invalid number of arguments. Call !plancli without arguments to see proper format example")
            return

        await ctx.send(content=response)


async def setup(bot):
    await bot.add_cog(Calendar(bot))
