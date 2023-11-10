from discord.ext import commands


class Faq(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Says hi', aliases=['hi'])
    async def hello(self, ctx):
        await ctx.send(content='hi')

    @commands.command(brief='Sends the website of the UAIS', aliases=['site'])
    async def website(self, ctx):
        await ctx.send(content='https://uais.dev/')


async def setup(bot):
  await bot.add_cog(Faq(bot))
