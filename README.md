# Project: University Of Alberta Artificial Intelligence Society Discord Chat Bot

## Running
1. Clone the repository
2. Create a file named .env (in the same directory as this README file), copy everything from .env.example to the file and fill in your bot Token
3. Run main.py

## Ideas 
1. FAQ feature
2. GPT AI integration
3. Automate announcements/club schedule events.
4. Bulk role assignment
5. Automate rsvp, maybe through discord message reactions.
6. Logging 
7. Extensive docs for the code

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
