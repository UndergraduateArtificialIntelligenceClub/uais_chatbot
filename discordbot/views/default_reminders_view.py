import discord

select_offsets = [
    discord.SelectOption(label="1 week before", value="10080"),
    discord.SelectOption(label="3 days before", value="4320"),
    discord.SelectOption(label="1 day before", value="1440"),
    discord.SelectOption(label="12 hours before", value="720"),
    discord.SelectOption(label="6 hours before", value="360"),
    discord.SelectOption(label="3 hours before", value="180"),
    discord.SelectOption(label="1 hour before", value="60"),
    discord.SelectOption(label="30 minutes before", value="30"),
    discord.SelectOption(label="15 minutes before", value="15"),
    discord.SelectOption(label="5 minutes before", value="5"),
]


class DefaultRemindersView(discord.ui.View):

    def __init__(self, user: discord.User):
        super().__init__(timeout=1800)
        self.user = user
        self.minute_offsets = None
        self.offsets_submitted = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """
        Only the user passed to constructor can use this view
        """
        return interaction.user == self.user

    @discord.ui.button(label="Submit", emoji="✅", style=discord.ButtonStyle.grey, disabled=True, row=0)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Clear items, respond to interaction, and stop
        self.clear_items()
        await interaction.response.defer()
        await interaction.delete_original_response()
        self.stop()

    @discord.ui.select(cls=discord.ui.Select, placeholder='Custom remind times (default=1d, 3h, 15m)', options=select_offsets, min_values=0, max_values=10, row=1)
    async def select_remind_times(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.minute_offsets = [int(value) for value in select.values]
        self.offsets_submitted = True
        submit_button = self.children[0]
        submit_button.disabled = False
        submit_button.style = discord.ButtonStyle.green
        await interaction.response.edit_message(view=self, content=f'**You selected offsets (in minutes):** {", ".join(select.values)}')
