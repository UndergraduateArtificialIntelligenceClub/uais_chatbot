import os

from discord.ext import commands


class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Error unloading {cog}: {e}')
            return
        await ctx.send(f'Unloaded {cog}')

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, cog: str):
        try:
            await self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Error loading {cog}: {e}')
            return
        await ctx.send(f'Loaded {cog}')

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(f'cogs.{cog}')
            await self.bot.load_extension(f'cogs.{cog}')
        except Exception as e:
            await ctx.send(f'Error reloading {cog}: {e}')
            return
        await ctx.send(f'Reloaded {cog}')

    @commands.command(name='listcogs')
    @commands.is_owner()
    async def list_cogs(self, ctx):
        msg = 'List of cogs:'
        print(os.listdir('discordbot/cogs'))
        for entry in os.listdir('discordbot/cogs'):
            # TODO: Could add a check to see if the file contains a cog class
            if entry.endswith('.py'):
                msg += f'\n- {entry[:-3]}'
        await ctx.send(msg)


async def setup(bot):
    await bot.add_cog(Admin(bot))
