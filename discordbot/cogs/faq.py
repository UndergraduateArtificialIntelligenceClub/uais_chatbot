from discord.ext import commands


class Faq(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Says hi', aliases=['hi'])
    async def hello(self, ctx):
        await ctx.send(content='hi')


async def setup(bot):
  await bot.add_cog(Faq(bot))
