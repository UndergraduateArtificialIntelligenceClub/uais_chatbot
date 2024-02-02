from discord.ext import commands
import discord
from asyncio import TimeoutError

### TODO: clean up delete function, change command aliases, redo bot end messages, maybe make a new cog file for member name listing, add ability to specify category for creating individual text/voice channels
"""Create categories for channels, and try do for different channels like voice vs text"""

class Channels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Makes a new text or voice channel', aliases=['create_channel'])
    @commands.has_permissions(administrator=True)
    async def create(self, ctx, type, *, name=None):
        guild = ctx.guild
        if type.lower() not in ['voice','text','category','cat']:
            await ctx.send(f'Invalid type. Please try again:`!create_channel voice [channel name]`, `!create_channel text [channel name]`, `!create_channel category [category name]`')
            return
        
        if name is None:
            if type.lower() in ['voice', 'text']:
                await ctx.send(f'You did not include a name for your {type} channel. Please try again: `!create_channel {type} [channel name]`')
            else:
                await ctx.send(f'You did not include a name for your category. Please try again: `!create_channel category [category name]`')
            return
        
        if type.lower() in ['cat', 'category']:
            category = discord.utils.get(guild.categories, name=name)

            if category:
                await ctx.send(f"A category with the name '{name}' already exists.")
                return

            await guild.create_category(name)
            await ctx.send(f"Created a category named {name}")
        
        else:
            if type.lower() == 'text':
                channel_create_function = guild.create_text_channel
                channel_type_name = 'text'
            elif type.lower() == 'voice':
                channel_create_function = guild.create_voice_channel
                channel_type_name = 'voice'
            else:
                await ctx.send('Invalid channel type. Please specify "text" or "voice".')
                return
            
            await ctx.send(f"Do you want this {channel_type_name} channel to be in a category? If yes, please specify the category name, otherwise type 'n'")
            category_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)

            if category_name.content.lower() == 'n':
                category = None
            else:
                category = discord.utils.get(ctx.guild.categories, name=category_name.content)
                if category is None:
                    await ctx.send("Invalid category name. Please try the command again.")
                    return
            
            existing_channel = discord.utils.get(category.channels if category else guild.channels, name=name)
            if existing_channel:
                await ctx.send(f"A {channel_type_name} channel with the name '{name}' already exists")
                return

            await channel_create_function(name, category=category)
            await ctx.send(f"Created a {channel_type_name} channel named {name}{' in the category ' + category.name if category else ''}")


    @commands.command(brief='Deletes a channel', aliases=['del'])
    @commands.has_permissions(administrator=True)
    async def delete(self, ctx, name=None):
        guild = ctx.guild
        if name is None:
            await ctx.send('You did not provide a name for the channel to delete. Please try again: `!delete [channel name]`')
            return

        await ctx.send("Is this channel within a category? If yes, please specify the category name, otherwise type 'n'")
        category_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
        if category_name.content.lower() == 'n':
            category = None
        else:
            category = discord.utils.get(ctx.guild.categories, name=category_name.content)
            if category is None:
                await ctx.send("Invalid category name. Please try the command again.")
                return
        
        channel = discord.utils.get(category.channels if category else guild.channels, name=name)
        if channel is not None:
            await channel.delete()
            await ctx.send(f"Deleted a channel named {name}")
        else:
            await ctx.send(f"Channel '{name}' does not exist.")
            
    
    @commands.command(brief='Create or delete a team category and associated channels', aliases=[])
    @commands.has_permissions(administrator=True)
    async def team(self, ctx, action, *, name=None):
        guild = ctx.guild

        if name is None:
            await ctx.send('You did not include a name for your team. Please try again: `!team create [team name]` or `!team delete [team name]`')
            return

        if action.lower() == "create":
            role = discord.utils.get(ctx.guild.roles, name=name)
            if not role:
                await ctx.send(f"The role {name} does not exist.")
                return

            category_name = name + ' team'
            category = discord.utils.get(guild.categories, name=category_name)
            if category:
                await ctx.send(f"A category with the name '{category_name}' already exists.")
                return

            await ctx.send("Would you like to customize the voice and text channel names? y/n? (Default names would be applied otherwise)")
            default = True
            try:
                customcheck = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
                if customcheck.content.upper() == 'Y':
                    default = False
            except TimeoutError:
                await ctx.send("Timed out. Please try the command again.")
                return

            if default:
                text_channel_name = name.replace(' ', '-') + '-general'
                voice_channel_name = name.replace(' ', '-') + '-meeting'
            else:
                await ctx.send("Please enter the name for the text channel:")
                try:
                    text_channel_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
                    text_channel_name = text_channel_name.content
                except TimeoutError:
                    await ctx.send("Timed out. Please try the command again.")
                    return

                await ctx.send("Please enter the name for the voice channel:")
                try:
                    voice_channel_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)
                    voice_channel_name = voice_channel_name.content
                except TimeoutError:
                    await ctx.send("Timed out. Please try the command again.")
                    return

            category = await guild.create_category_channel(name=category_name)
            text = await category.create_text_channel(text_channel_name)
            voice = await category.create_voice_channel(voice_channel_name)

            await text.set_permissions(role, read_messages=True, send_messages=True)
            await voice.set_permissions(role, connect=True)

            await text.set_permissions(ctx.guild.default_role, read_messages=False, send_messages=False)
            await voice.set_permissions(ctx.guild.default_role, connect=False)

            await ctx.send(f"Created a team category for {name} team")
            await text.send(f"Welcome to the {name.upper()} team channel!")

        elif action.lower() in ["delete","del"]:
            category = discord.utils.get(guild.categories, name=name)

            if category:
                for channel in category.channels:
                    await channel.delete()

                await category.delete()

                await ctx.send(f"Category '{name}' and all channels within it have been deleted.")
            else:
                await ctx.send(f"Category '{name}' not found.")
        else:
            await ctx.send("Invalid action. Please use 'create' or 'delete'.")



async def setup(bot):
  await bot.add_cog(Channels(bot))
  
