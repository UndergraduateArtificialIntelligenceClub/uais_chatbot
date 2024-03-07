from discord.ext import commands
import discord


class Names(commands.Cog):
    def __init__(self, bot):
        self.bot = bot    

    @commands.command(brief='List the names of all categories in the server', aliases= ['list_cat', 'cat_names'])
    @commands.has_permissions(administrator=True)
    async def category_names(self, ctx):
        guild = ctx.guild
        category_names = [category.name for category in guild.categories]
        cat_str = "\n".join(category_names)
        await ctx.send(f"Category names in the server: \n```\n{cat_str}\n```")

    @commands.command(brief='Lists all names of channels in a category', aliases=['list_cat_channels'])
    @commands.has_permissions(administrator=True)
    async def cat_channel_names(self, ctx, *, category_name=None):
        guild = ctx.guild

        if category_name is None:
            await ctx.send('You did not specify a category name.')
            return

        category = discord.utils.get(guild.categories, name=category_name)

        if category is None:
            await ctx.send(f"The category '{category_name}' does not exist.")
            return

        channel_names = [channel.name for channel in category.channels]

        if channel_names:
            await ctx.send(f"Channels in the category '{category_name}':")
            await ctx.send('\n'.join(channel_names))
        else:
            await ctx.send(f"There are no channels in the category '{category_name}'.")

    @commands.command(brief='Lists all channels not in a category', aliases=['list_extra_channels'])
    @commands.has_permissions(administrator=True)
    async def extra_names(self, ctx):
        guild = ctx.guild

        uncategorized_channels = [channel.name for channel in guild.channels if not channel.category and isinstance(channel, (discord.TextChannel, discord.VoiceChannel))]

        if uncategorized_channels:
            await ctx.send("Text and voice channels not in any category:")
            await ctx.send('\n'.join(uncategorized_channels))
        else:
            await ctx.send("There are no text and voice channels not in any category.")

    
    @commands.command(brief='List the names of all roles in the server', aliases= ['roles'])
    @commands.has_permissions(administrator=True)
    async def role_names(self, ctx):
        guild = ctx.guild
        roles = guild.roles

        role_names = [role.name for role in roles]
        roles_str = "\n".join(role_names)

        await ctx.send(f"Roles in the server:\n```\n{roles_str}\n```")   
    
    @commands.command(brief='List the users with admins permissions', aliases = ['admins'])
    @commands.has_permissions(administrator=True)
    async def list_admins(self, ctx):
        admins = []
        
        for member in ctx.guild.members:
            if any(role.permissions.administrator for role in member.roles):
                admins.append(member.display_name)

        if admins:
            admins_str = '\n '.join(admins)
            await ctx.send(f"Members with Administrator permissions:\n```\n{admins_str}\n```")
        else:
            await ctx.send("No members with Administrator permissions found.")

    @commands.command(brief='List the members of UAIS', aliases = ['members', 'humans'])
    @commands.has_permissions(administrator=True)
    async def list_members(self, ctx):
        members = [member.display_name for member in ctx.guild.members if not member.bot]
        members_str = '\n'.join(members)
        await ctx.send(f"Members in the server:\n```\n{members_str}\n```")

    @commands.command(brief='List the bots of UAIS', aliases = ['bots'])
    @commands.has_permissions(administrator=True)
    async def list_bots(self, ctx):
        bots = [member.display_name for member in ctx.guild.members if member.bot]
        bots_str = '\n'.join(bots)
        await ctx.send(f"Members in the server:\n```\n{bots_str}\n```")
    
    @commands.command(brief='Lists all users in the server including bots', aliases = ['everyone'])
    @commands.has_permissions(administrator=True)
    async def list_everyone(self, ctx):
        members = [member.display_name for member in ctx.guild.members]
        members_str = '\n'.join(members)
        await ctx.send(f"Members in the server:\n```\n{members_str}\n```")

    @commands.command(brief='List the users with provided role', aliases = ['rolecall', 'teammates'])
    @commands.has_permissions(administrator=True)
    async def list_team(self, ctx, team_name=None):
        if team_name == None:
            await ctx.send('You did not include role name. Please try again: `!rolecall [team role name]`')
            return
        role = discord.utils.get(ctx.guild.roles, name=team_name)
        team = []
        if role:
            for member in ctx.guild.members:
                if role in member.roles:
                    team.append(member.display_name)
        if team:
            team_str = '\n '.join(team)
            await ctx.send(f"Members with role '{team_name}':\n```\n{team_str}\n```")
        else:
            await ctx.send(f"No members with role '{team_name}' found.")



async def setup(bot):
  await bot.add_cog(Names(bot))