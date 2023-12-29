import discord
from datetime import datetime, timedelta


class EventNamingModal(discord.ui.Modal, title="Name The Event"):
    def __init__(self, initial_summary="", initial_description="", initial_location=""):
        super().__init__()
        # Modals remember values
        self.summary.default = initial_summary
        self.description.default = initial_description
        self.location.default = initial_location

    summary = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Title",
        required=True,
        placeholder="Event Summary"
    )

    description = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Description",
        required=False,
        placeholder="Event Description (optional)"
    )

    location = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Location",
        required=False,
        placeholder="Event Location (optional)"
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="**Event creation menu:**  (Title and Description saved)")


class EventDateModal(discord.ui.Modal, title="Set The Date"):
    def __init__(self, initial_day="", initial_month="", initial_year="", initial_time="", initial_duration=""):
        super().__init__()
        # Modals remember values. If none are entered, default ones are shown
        self.day.default = initial_day or str(datetime.now().day)
        self.month.default = initial_month or datetime.now().strftime("%B")
        self.year.default = initial_year or str(datetime.now().year)
        self.time.default = initial_time or datetime.now().strftime("%I:%M %p").lstrip("0")
        self.duration.default = initial_duration or "60m"

    day = discord.ui.TextInput(
        label="Enter day (1-31)",
        min_length=1,
        max_length=2
    )

    month = discord.ui.TextInput(
        label="Enter month (1-12 or name)",
        min_length=1,
        max_length=9
    )

    year = discord.ui.TextInput(
        label="Enter year",
        min_length=1,
        max_length=15
    )

    time = discord.ui.TextInput(
        label="Enter time (e.g. 14:00 or 2:00 PM)",
        min_length=1,
        max_length=15
    )

    duration = discord.ui.TextInput(
        label="Enter duration (e.g. 30m or 0.5h)",
        min_length=1,
        max_length=4
    )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.edit_message(content="**Event creation menu:**  (Date and Time saved)")


def return_valid_date(day, month, year):
    # Dictionary to map month names to numbers
    month_mapping = {
        'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
        'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
    }

    try:
        # Convert month name to number if necessary
        if isinstance(month, str) and not month.isdigit():
            month = month.lower()
            # Month not found = return -1, will cause ValueError in datetime
            month = month_mapping.get(month, -1)

        # Create date object
        date = datetime(int(year), int(month), int(day))
        return date

    except ValueError:
        return False


def return_valid_time(time: str):
    try:
        if len(time.split(' ')) == 2:  # Assuming 12-hour format with AM/PM
            time = datetime.strptime(time, "%I:%M %p")
        else:  # Assuming 24-hour format
            time = datetime.strptime(time, "%H:%M")
        return time
    except ValueError:
        return False


def return_valid_duration(duration: str):
    try:
        if 'm' in duration.lower():
            duration_minutes = int(duration.replace('m', ''))
        elif 'h' in duration.lower():
            duration_hours = float(duration.replace('h', ''))
            duration_minutes = int(duration_hours * 60)
        else:
            return False
    except ValueError:
        return False

    return duration_minutes


class EventCreationView(discord.ui.View):

    def __init__(self, user: discord.User):
        super().__init__(timeout=1800)
        self.user = user
        self.event_data = {
            "summary": "",
            "description": "",
            "location": "",
            "day": "",
            "month": "",
            "year": "",
            "time": "",
            "duration": "",
            "start_time": "",
            "end_time": ""
        }
        self.name_modal_submitted = False
        self.date_modal_submitted = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Only the user passed to constructor can use this view
        """
        return interaction.user == self.user

    async def check_readiness(self, interaction: discord.Interaction):
        """
        Makes the submit button clickable if all conditions are met
        """
        # Submit button disabled by default
        submit_button = self.children[2]
        submit_button.disabled = True
        submit_button.style = discord.ButtonStyle.grey

        if self.date_modal_submitted:
            error_payload = self.validate_date_modal()

            if error_payload:
                self.children[1].style = discord.ButtonStyle.danger
                await interaction.edit_original_response(view=self, content=error_payload)
                return

        if not self.date_modal_submitted or not self.name_modal_submitted:
            # Not all required data filled out, return
            await interaction.edit_original_response(view=self)
            return

        # All checks passed, unlocking submit button
        submit_button.disabled = False
        submit_button.style = discord.ButtonStyle.green
        await interaction.edit_original_response(view=self, content="**Ready to add event to calendar**")

    def validate_date_modal(self):
        """
        If date modal has correct values, returns nothing and calculates start_time and end_time
        If incorrect value is encountered, returns a string specifying where
        """
        event_data = self.event_data
        error_payload = ""

        start_date = return_valid_date(
            event_data["day"], event_data["month"], event_data["year"])
        start_time = return_valid_time(event_data["time"])
        duration_minutes = return_valid_duration(event_data["duration"])

        if not start_date:
            error_payload += "**Error:** invalid day, month or year entered"
        if not start_time:
            error_payload += "\n**Error:** invalid time entered"
        if not duration_minutes:
            error_payload += "\n**Error:** invalid duration entered"

        if not error_payload:
            # Combine date and time for start_time
            start_time = start_time.replace(
                year=start_date.year, month=start_date.month, day=start_date.day)

            # Calculate end time in respect to duration
            end_time = start_time + timedelta(minutes=duration_minutes)

            # Prepare event information
            self.event_data["start_time"] = start_time.isoformat()
            self.event_data["end_time"] = end_time.isoformat()

        return error_payload

    @discord.ui.button(label="Set Title", emoji="✏️", style=discord.ButtonStyle.primary)
    async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        # On click, create the modal and send it to the user
        modal = EventNamingModal(
            initial_summary=self.event_data["summary"],
            initial_description=self.event_data["description"],
            initial_location=self.event_data["location"]
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        self.event_data.update({
            "summary": modal.summary.value,
            "description": modal.description.value,
            "location": modal.location.value
        })
        self.name_modal_submitted = True

        # Make the button gray (clicked)
        button.style = discord.ButtonStyle.gray
        await self.check_readiness(interaction)

    @discord.ui.button(label="Set Date", emoji="📅", style=discord.ButtonStyle.primary)
    async def set_date(self, interaction: discord.Interaction, button: discord.ui.Button):
        # On click, create the modal and send it to the user
        modal = EventDateModal(
            initial_day=self.event_data["day"],
            initial_month=self.event_data["month"],
            initial_year=self.event_data["year"],
            initial_time=self.event_data["time"],
            initial_duration=self.event_data["duration"]
        )

        await interaction.response.send_modal(modal)
        await modal.wait()

        self.event_data.update({
            "day": modal.day.value,
            "month": modal.month.value,
            "year": modal.year.value,
            "time": modal.time.value,
            "duration": modal.duration.value
        })
        self.date_modal_submitted = True

        # Make the button gray (clicked)
        button.style = discord.ButtonStyle.gray
        await self.check_readiness(interaction)

    @discord.ui.button(label="Submit", emoji="✅", style=discord.ButtonStyle.grey, disabled=True)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Clear items, respond to interaction, and stop
        self.clear_items()
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()
