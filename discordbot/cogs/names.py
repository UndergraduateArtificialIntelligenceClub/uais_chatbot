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
    
    @commands.command(brief='List the names of all roles in the server', aliases= ['roles'])
    @commands.has_permissions(administrator=True)
    async def category_names(self, ctx):
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