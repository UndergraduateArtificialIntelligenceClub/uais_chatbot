import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from discord.ext import commands

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


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

            # print("Getting the upcoming 10 events")
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
        await ctx.send(content="Foo")

    @commands.command(brief='Plans an event from one text command call', aliases=['plc', 'planc', 'plcli'])
    async def plancli(self, ctx):
        event = {
            'summary': 'Test event',
            'location': 'University of Alberta',
            'description': 'Description',
            'start': {
                'dateTime': '2023-12-20T09:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'end': {
                'dateTime': '2023-12-21T17:00:00-07:00',
                'timeZone': 'America/Los_Angeles',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        event = self.service.events().insert(calendarId='primary', body=event).execute()
        await ctx.send(content=f"Event created: {event.get('htmlLink')}")


async def setup(bot):
    await bot.add_cog(Calendar(bot))
