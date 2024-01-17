import os
import asyncio
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ['DISCORD_TOKEN']
PREFIX = os.environ['COMMAND_PREFIX']

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


# Comment out cogs you do not need during development
async def load_extensions():
    await bot.load_extension(f"cogs.faq")
    # await bot.load_extension(f"cogs.googlecalendar")
    await bot.load_extension(f"cogs.channels")
    await bot.load_extension(f"cogs.names")


async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
