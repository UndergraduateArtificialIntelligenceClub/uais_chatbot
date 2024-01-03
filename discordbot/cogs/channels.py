from discord.ext import commands
import discord

"""Create categories for channels, and try do for different channels like voice vs text"""
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.reactions = True
intents.members = True

class Channels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Makes a new text channel', aliases=['create text'])
    @commands.has_permissions(administrator=True)
    async def create_text(self,ctx, *, name=None):
        guild = ctx.message.guild
        if name == None:
            await ctx.send('You did not inlcude a name for your channel. Please try again: `!create text [channel name]`')
        else:
            await guild.create_text_channel(name)
            await ctx.send(f"Created a text channel named {name}")

    # @commands.command(brief='Makes a new voice channel', aliases=['create voice'])
    # @commands.has_permissions(administrator=True)
    # async def create_voice(self,ctx, *, name=None):
    #     guild = ctx.message.guild
    #     if name == None:
    #         await ctx.send('You did not inlcude a name for your channel. Please try again: `!create voice [channel name]`')
    #     else:
    #         await guild.create_voice_channel(name)
    #         await ctx.send(f"Created a voice channel named {name}")

    
    @commands.command(brief='Delete a category and all channels within it', aliases=['del_cat'])
    @commands.has_permissions(administrator=True)
    async def delete_category_and_channels(self, ctx, *, category_name):
        guild = ctx.guild

        # Find the category by name
        category = discord.utils.get(guild.categories, name=category_name)

        if category:
            # Delete all channels within the category
            for channel in category.channels:
                await channel.delete()

            # Delete the category itself
            await category.delete()

            await ctx.send(f"Category '{category_name}' and all channels within it have been deleted.")
        else:
            await ctx.send(f"Category '{category_name}' not found.")

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
            await ctx.send("Making category...")
            category = await guild.create_category_channel(name=name+' team')
            for member in guild.members:
                if role in member.roles:
                    print(f"Granting permissions to {member.display_name}")
                    await category.set_permissions(member, read_messages=True, connect=True)
                else:
                    print(f"Revoking permissions from {member.display_name}")
                    await category.set_permissions(member, read_messages=False, connect=False)


            text = await category.create_text_channel(name + '-general')
            voice = await category.create_voice_channel(name + '-meeting')

            await text.set_permissions(role, read_messages=True, send_messages=True)
            await voice.set_permissions(role, connect=True)

            await ctx.send(f"Created a team category for {name}")
        else:
            await ctx.send(f"The role {name} does not exist.")


    @commands.command(brief='Get the names of all categories in the server')
    async def catnames(self, ctx):
        guild = ctx.guild
        category_names = [category.name for category in guild.categories]
        await ctx.send(f"Category names in the server: {', '.join(category_names)}")
    
    @commands.command(brief='List the users with admins permissions')
    async def list_members(self, ctx):
        admins = []
        
        for member in ctx.guild.members:
            if any(role.permissions.administrator for role in member.roles):
                admins.append(member.display_name)

        if admins:
            await ctx.send(f"Members with Administrator permissions: {', '.join(admins)}")
        else:
            await ctx.send("No members with Administrator permissions found.")
        #await ctx.guild.chunk()
        members = [member.display_name for member in ctx.guild.members]
        await ctx.send(f"Members in the server: {', '.join(members)}")

async def setup(bot):
  await bot.add_cog(Channels(bot))
  
