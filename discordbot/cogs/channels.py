from discord.ext import commands
import discord
import asyncio

### TODO: clean up delete function, change command aliases, redo bot end messages, maybe make a new cog file for member name listing
"""Create categories for channels, and try do for different channels like voice vs text"""

class Channels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Makes a new text channel', aliases=['text'])
    @commands.has_permissions(administrator=True)
    async def create_text(self,ctx, *, name=None):
        guild = ctx.message.guild
        if name == None:
            await ctx.send('You did not inlcude a name for your channel. Please try again: `!create text [channel name]`')
        else:
            await guild.create_text_channel(name)
            await ctx.send(f"Created a text channel named {name}")
    
    @commands.command(brief='Makes a new voice channel', aliases=['voice'])
    @commands.has_permissions(administrator=True)
    async def create_text(self,ctx, *, name=None):
        guild = ctx.message.guild
        if name == None:
            await ctx.send('You did not inlcude a name for your channel. Please try again: `!create text [channel name]`')
        else:
            await guild.create_voice_channel(name)
            await ctx.send(f"Created a voice channel named {name}")

    @commands.command(brief='Deletes a channel', aliases=['del'])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, name=None):
        guild = ctx.guild
        channel = discord.utils.get(guild.channels, name=name)
        if channel is not None:
            await channel.delete()
            await ctx.send(f"Deleted a channel named {name}")
        else:
            await ctx.send("Channel",name,"does not exist.")
    
 
    @commands.command(brief='Creates a category for a team with a text channel and voice channel', aliases=['cat', 'team'])
    @commands.has_permissions(administrator=True)
    async def category(self, ctx, *, name=None): 
        guild = ctx.guild
        if name is None:
            await ctx.send('You did not include a name for your channel. Please try again: `!category [team role name]`')
            return

        role = discord.utils.get(ctx.guild.roles, name=name)
        if role:
            await ctx.send("Would you like to customize the voice and text channel names? y/n? (Default names would be applied otherwise)")
            default = True
            try:
                customcheck = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout= 60)
                if customcheck.content.upper() == 'Y':
                    default = False
            except asyncio.TimeoutError:
                await ctx.send("Timed out. Please try the command again.")
                return
            
            
            if default:
                text_channel_name =name + '-general'
                voice_channel_name = name + '-meeting'

            else:
                
                await ctx.send("Please enter the name for the text channel:")
                try:
                    text_channel_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
                    text_channel_name = text_channel_name.content
                except asyncio.TimeoutError:
                    await ctx.send("Timed out. Please try the command again.")
                    return
                
                await ctx.send("Please enter the name for the voice channel:")
                try:
                    voice_channel_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
                    voice_channel_name = voice_channel_name.content
                except asyncio.TimeoutError:
                    await ctx.send("Timed out. Please try the command again.")
                    return
                #await ctx.send("text name and voice: ", text_channel_name, type(voice_channel_name))
                
            
                
            await ctx.send("Making category...") 
            category = await guild.create_category_channel(name=name+' team')  
            text = await category.create_text_channel(text_channel_name)
            voice = await category.create_voice_channel(voice_channel_name) 

            await text.set_permissions(role, read_messages=True, send_messages=True)
            await voice.set_permissions(role, connect=True)

            await text.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
            await voice.set_permissions(ctx.guild.default_role, connect = False)

            await ctx.send(f"Created a team category for {name} team")
            await text.send(f"Welcome to the {name.upper()} team channel!")
        
        else:
            await ctx.send(f"The role {name} does not exist.")


    @commands.command(brief='Delete a category and all channels within it', aliases=['del_cat', 'del_team'])
    @commands.has_permissions(administrator=True)
    async def delete_category(self, ctx, *, category_name):
        guild = ctx.guild
        category = discord.utils.get(guild.categories, name=category_name)

        if category:
            for channel in category.channels:
                await channel.delete()

            await category.delete()

            await ctx.send(f"Category '{category_name}' and all channels within it have been deleted.")
        else:
            await ctx.send(f"Category '{category_name}' not found.")

async def setup(bot):
  await bot.add_cog(Channels(bot))
  
