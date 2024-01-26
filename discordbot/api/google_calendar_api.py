import os
import json
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

    def get_events(self, max_results=10):
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

            return events

        except HttpError as error:
            return f"An error occured: {error}"

    def create_event(self, summary, location, description, start_time: datetime, end_time: datetime, tags: list = None):
        # Example arguments:
        # Test event, University of Alberta, Description, datetime start time, datetime end time, ["tag1"]

        if not summary or not start_time or not end_time:
            return None

        # Convert tags list to a JSON string
        tags_json = json.dumps(tags) if tags is not None else ''

        event = {
            'summary': summary,
            'location': location,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': TIMEZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'extendedProperties': {
                'private': {
                    'tags': tags_json  # Additional info to store with event
                }
            }
        }

        try:
            event = self.service.events().insert(calendarId='primary', body=event).execute()
        except HttpError as error:
            return f"An error occured: {error}"

        return f"Event created: {event.get('htmlLink')}"
