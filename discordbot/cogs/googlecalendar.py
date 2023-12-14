import os
import discord
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TIMEZONE = os.environ['TIMEZONE']

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class EventNamingModal(discord.ui.Modal, title="Name The Event"):

    event_summary = discord.ui.TextInput(
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


class EventDateModal(discord.ui.Modal, title="Set The Date"):

    day = discord.ui.TextInput(
        label="Enter day (1-31)",
        default=datetime.now().day,
        min_length=1,
        max_length=2
    )

    month = discord.ui.TextInput(
        label="Enter month (1-12 or name)",
        default=datetime.now().month,
        min_length=1,
        max_length=15
    )

    year = discord.ui.TextInput(
        label="Enter year",
        default=datetime.now().year,
        min_length=1,
        max_length=15
    )

    time = discord.ui.TextInput(
        label="Enter time (e.g. 14:00 or 2:00 PM)",
        default=datetime.now().strftime("%I:%M %p").lstrip("0"),
        min_length=1,
        max_length=15
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="**Event creation menu:**  (Date and Time saved)")


class EventCreationView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=3600)
        self.name_modal = None
        self.time_modal = None

    @discord.ui.button(label="Set Title", emoji="✏️", style=discord.ButtonStyle.primary)
    async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        # On click, create the modal and send it to the user
        modal = EventNamingModal()
        await interaction.response.send_modal(modal)
        # Wait until user submits info
        await modal.wait()
        self.name_modal = modal
        # Make it gray (clicked)
        button.style = discord.ButtonStyle.gray
        await self.check_readiness(interaction)

    @discord.ui.button(label="Set Date", emoji="📅", style=discord.ButtonStyle.primary)
    async def set_date(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = EventDateModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.time_modal = modal
        button.style = discord.ButtonStyle.gray
        await self.check_readiness(interaction)

    async def check_readiness(self, interaction: discord.Interaction):
        name_modal, time_modal = self.name_modal, self.time_modal
        # Submit button disabled by default
        submit_button = self.children[2]
        submit_button.disabled = True
        submit_button.style=discord.ButtonStyle.grey

        if time_modal:
            error_payload = ""
            day, month, year, time = time_modal.day.value, time_modal.month.value, time_modal.year.value, time_modal.time.value

            if not self.is_valid_date(day, month, year):
                error_payload += "**Error:** invalid day, month or year entered"
            if not self.is_valid_time(time):
                error_payload += "\n**Error:** invalid time entered"

            if error_payload:
                self.children[1].style = discord.ButtonStyle.danger
                await interaction.edit_original_response(view=self, content=error_payload)
                return

        if not name_modal or not time_modal:
            await interaction.edit_original_response(view=self)
            return

        # All checks passed, unlocking submit button
        submit_button.disabled = False
        submit_button.style=discord.ButtonStyle.green
        await interaction.edit_original_response(view=self, content="**Ready to add event to calendar**")


    def is_valid_date(self, day, month, year):
        try:
            datetime(int(year), int(month), int(day))
            return True
        except ValueError:
            return False

    def is_valid_time(self, time_str):
        try:
            if len(time_str.split(' ')) == 2:  # Assuming 12-hour format with AM/PM
                datetime.strptime(time_str, "%I:%M %p")
            else:  # Assuming 24-hour format
                datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

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
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': arguments[4],
                'timeZone': TIMEZONE,
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
