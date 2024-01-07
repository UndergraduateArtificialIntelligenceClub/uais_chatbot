import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
TIMEZONE = os.environ['TIMEZONE']

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarAPI:
    def __init__(self):
        self.service = self.initialize_service()

    def initialize_service(self):
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
            return build("calendar", "v3", credentials=creds)
        except HttpError as error:
            print(f"Google calendar initialization failed: {error}")
            return None

    def list_events(self, max_results=10):
        try:
            # Call the Calendar API
            now = datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time

            # Getting the upcoming max_results events
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                return "No upcoming events found."

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

            return payload

        except HttpError as error:
            return f"An error occured: {error}"

    def create_event(self, event_data):
        # Summary,Location,Description,Start time,End time
        # Test event,University of Alberta,Description,2023-12-20T09:00:00,2023-12-21T17:00:00

        arguments = event_data.split(',')
        if len(arguments) != 5:
            return None

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
            return f"An error occured: {error}"

        return f"Event created: {event.get('htmlLink')}"
