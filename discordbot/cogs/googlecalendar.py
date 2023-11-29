import datetime
import os
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

    @commands.command(brief='Lists 10 upcoming Google Calendar events', aliases=['calendar', 'ev'])
    async def events(self, ctx):
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
            service = build("calendar", "v3", credentials=creds)

            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

            # print("Getting the upcoming 10 events")
            events_result = (
                service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                await ctx.send(content="No upcoming events found.")
                return

            # Sends the start and name of the next 10 events
            payload = ""
            for event in events:
                start = event["start"].get(
                    "dateTime", event["start"].get("date"))
                payload += f"{start} {event['summary']}\n"

            await ctx.send(content=payload)

        except HttpError as error:
            await ctx.send(content=f"An error occured: {error}")

    @commands.command(brief='Opens event creation menu')
    async def plan(self, ctx):
        # TODO:implement
        await ctx.send(content="Foo")


async def setup(bot):
    await bot.add_cog(Calendar(bot))
