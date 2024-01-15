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

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


async def load_extension():
    for filename in os.listdir("discordbot/cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

async def reload(ctx):
    # Reloads the file, thus updating the Cog class.
    bot.reload_extension("cogs.tracking")


async def main():
    async with bot:
        await load_extension()
        await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
