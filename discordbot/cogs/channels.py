from discord.ext import commands
import discord

"""Create categories for channels, and try do for different channels like voice vs text"""

class Channels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Makes a new text channel', aliases=['create text'])
    async def create_text(self,ctx, *, name=None):
        guild = ctx.message.guild
        if name == None:
            await ctx.send('You did not inlcude a name for your channel. Please try again: `!create text [channel name]`')
        else:
            await guild.create_text_channel(name)
            await ctx.send(f"Created a text channel named {name}")

    @commands.command(brief='Makes a new voice channel', aliases=['create voice'])
    async def create_voice(self,ctx, *, name=None):
        guild = ctx.message.guild
        if name == None:
            await ctx.send('You did not inlcude a name for your channel. Please try again: `!create voice [channel name]`')
        else:
            await guild.create_voice_channel(name)
            await ctx.send(f"Created a voice channel named {name}")

    @commands.command(brief='Deletes a channel', aliases=['del'])
    async def delete(self, ctx, name=None):
        guild = ctx.guild
        channel = discord.utils.get(guild.channels, name=name)
        if channel is not None:
            await channel.delete()
            await ctx.send(f"Deleted a channel named {name}")
        else:
            await ctx.send("Channel",name,"does not exist.")

            


async def setup(bot):
  await bot.add_cog(Channels(bot))