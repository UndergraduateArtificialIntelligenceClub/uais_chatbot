# Project: University Of Alberta Artificial Intelligence Society Discord Chat Bot

## Running without Calendar API (if you don't want to touch it)
1. Clone the repository
2. Create a file named .env (in the same directory as this README file), copy everything from .env.example to the file and fill in your bot Token
3. Run main.py

## Running with Google Calendar API
1. Clone the repository
2. Create a file named .env (in the same directory as this README file), copy everything from .env.example to the file and fill in your bot Token
3. Set up google calendar API as seen here: https://developers.google.com/calendar/api/quickstart/python
4. Include credentials.json in the same directory as this README file
5. Uncomment line 26 in main.py
6. Run main.py
7. Authorize the google calendar API in the browser window that pops up if you are running for the first time

## Ideas 
1. FAQ feature
2. GPT AI integration
3. Automate announcements/club schedule events.
4. Bulk role assignment
5. Automate rsvp, maybe through discord message reactions.
6. Logging 
7. Extensive docs for the code
8. Admin cog

## Bot FAQ

### Docs
https://discordpy.readthedocs.io/

### Why is it bot.run, not client.run?
https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#discord.ext.commands.Bot

bot is a subclass of client that adds a bunch of useful functionality.

### What are cogs?
https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html?highlight=cogs
https://discordpy.readthedocs.io/en/stable/ext/commands/extensions.html#ext-commands-extensions

We will be using cogs and extensions (feature of discord.py) to develop this bot's functionality in an object-oriented way.
We can load and unload the bot's functionality without restarting the code by using extensions.

### What is asyncio?
https://discordpy.readthedocs.io/en/stable/migrating.html?highlight=asyncio#asyncio-event-loop-changes
