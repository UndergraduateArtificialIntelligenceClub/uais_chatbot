import os
import discord
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from discord.ext import commands

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventNamingModal(discord.ui.Modal, title="Name The Event"):

    event_title = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        required=True,
        placeholder="Event Summary"
    )

    event_description = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Description",
        required=False,
        placeholder="Event Description (optional)"
    )

    event_location = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Location",
        required=False,
        placeholder="Event Location (optional)"
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="**Event creation menu:**  (Title and Description saved)")


class EventCreationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=3600)
        self.event_title = None
        self.event_description = None
        self.event_location = None

    @discord.ui.button(label="Set Title", emoji="✏️", style=discord.ButtonStyle.primary)
    async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        # On click, create the textbox and send it to the user
        modal = EventNamingModal()
        await interaction.response.send_modal(modal)
        # Wait until user submits info
        await modal.wait()
        self.event_title = modal.event_title
        self.event_description = modal.event_description
        self.event_location = modal.event_location
        # Make it gray (clicked)
        button.style = discord.ButtonStyle.gray
        await interaction.edit_original_response(view=self)

    @discord.ui.button(label="Set Date", emoji="📅", style=discord.ButtonStyle.primary)
    async def set_date(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Set Time", emoji="🕒", style=discord.ButtonStyle.primary)
    async def set_time(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

    @discord.ui.button(label="Submit", emoji="✅", style=discord.ButtonStyle.grey, disabled=True)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


class Calendar(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        try:
            self.service = build("calendar", "v3", credentials=creds)
        except HttpError as error:
            print(f"Google calendar initialization failed: {error}")

    @commands.command(brief='Lists 10 (or specified number of) upcoming Google Calendar events', aliases=['calendar', 'ev'])
    async def events(self, ctx, events_num=10):
        if (not isinstance(events_num, int)) or (events_num < 1) or (events_num > 30):
            await ctx.send(content="Invalid number of events provided. Must be int and in [1, 30]")
            return

        try:
           # Call the Calendar API
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

            # print("Getting the upcoming events_num events")
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=events_num,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                await ctx.send(content="No upcoming events found.")
                return

            # Sends the start and name of the next events_num events
            payload = ""
            for event in events:
                # Get event start time
                start = event["start"].get(
                    "dateTime", event["start"].get("date"))
                # Convert to human readable format
                start_dt = datetime.fromisoformat(start)
                formatted_start = start_dt.strftime(
                    "%B %d, %Y, %I:%M %p").lstrip("0").replace(" 0", " ")

                payload += f"**{formatted_start}:** {event['summary']}\n"

            await ctx.send(content=payload)

        except HttpError as error:
            await ctx.send(content=f"An error occured: {error}")

    @commands.command(brief='Opens event creation menu', aliases=['pl'])
    async def plan(self, ctx):
        # TODO:implement
        event_creation_view = EventCreationView()
        await ctx.send(content="**Event creation menu:**", view=event_creation_view)
        await event_creation_view.wait()
        await ctx.send(content="View Submitted (final)")

    @commands.command(brief='Plans an event from one text command call. Call without arguments to see format', aliases=['plc', 'planc', 'plcli'])
    async def plancli(self, ctx, *, payload=""):
        if not payload:
            await ctx.send(content="!plancli Summary,Location,Description,Start time,End time\ne.g.\n!plancli Test event,University of Alberta,Description,2023-12-20T09:00:00-07:00,2023-12-21T17:00:00-07:00")
            return

        arguments = payload.split(',')
        if len(arguments) != 5:
            await ctx.send(content="Invalid number of arguments. Call !plancli without arguments to see proper format example")
            return

        event = {
            'summary': arguments[0],
            'location': arguments[1],
            'description': arguments[2],
            'start': {
                'dateTime': arguments[3],
                'timeZone': 'America/Edmonton',
            },
            'end': {
                'dateTime': arguments[4],
                'timeZone': 'America/Edmonton',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
        except HttpError as error:
            await ctx.send(content=f"An error occured: {error}")
            return

        await ctx.send(content=f"Event created: {event.get('htmlLink')}")


async def setup(bot):
    await bot.add_cog(Calendar(bot))
