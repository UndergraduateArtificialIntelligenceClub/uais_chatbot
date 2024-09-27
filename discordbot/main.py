import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import logging

# Determine the directory where main.py is located
base_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the log file, ensuring it's in the same directory as main.py
log_file_path = os.path.join(base_dir, 'bot_logs.txt')

# Configure logging
logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(name)s: %(message)s\n',
                    filename=log_file_path,
                    filemode='a')

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']
PREFIX = os.environ['COMMAND_PREFIX']

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


async def load_extensions():
    await bot.load_extension(f"cogs.admin")
    await bot.load_extension(f"cogs.faq")
    await bot.load_extension(f"cogs.auditlogs")
    await bot.load_extension(f"cogs.reactionroles")
    await bot.load_extension(f"cogs.googlecalendar")
    await bot.load_extension(f"cogs.channels")
    await bot.load_extension(f"cogs.names")
    await bot.load_extension(f"cogs.uai")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
