import os
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging

# Determine the directory where main.py is located
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the log file, ensuring it's in the same directory as main.py
log_file_path = os.path.join(base_dir, 'bot_logs.txt')

# Configure logging
logging.basicConfig(level=logging.DEBUG,  # Set log level to DEBUG
                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s\n',
                    filename=log_file_path,  # Save logs to bot_logs.txt in the current directory
                    filemode='a')  # Append to the log file

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']
PREFIX = os.environ['COMMAND_PREFIX']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


# Comment out cogs you do not need during development
async def load_extensions():
    await bot.load_extension(f"cogs.admin")
    await bot.load_extension(f"cogs.faq")
    await bot.load_extension(f"cogs.auditlogs")
    # await bot.load_extension(f"cogs.googlecalendar")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())