from discord.ext import commands
import json
import requests


JSON_DATA = 'data.json'

class StoreUserInfo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(brief='Links user discord account to github username.')
    async def setgithub(self, ctx, username=None):
        if not username:
            await ctx.send(content='Please provide a github username.')
            return
        discord_username = str(ctx.author.name)
        github_username = username
        
        r = requests.get(f'https://api.github.com/users/{github_username}')
        if r.status_code != 200:
            await ctx.send(content=f'Github username {github_username} does not exist.')
            return
        
        try:
            with open(JSON_DATA, 'r') as f:
                data = json.load(f)
        except:  # incorrect json format
            data = {}
        
        if discord_username in data:
            data[discord_username]['github'] = github_username
        else:
            data[discord_username] = {'github': github_username}
        
        with open(JSON_DATA, 'w') as f:
            f.write(json.dumps(data))
        
        await ctx.send(content=f'Linked {discord_username} to {github_username}')
        
    @commands.command(brief='Links user discord account to real name.')
    async def setname(self, ctx, name=None):
        if not name:
            await ctx.send(content='Please provide a name.')
            return
        discord_username = str(ctx.author.name)
        real_name = name
        
        try:
            with open(JSON_DATA, 'r') as f:
                data = json.load(f)
        except:
            data = {}
            
        if discord_username in data:
            data[discord_username]['name'] = real_name
        else:
            data[discord_username] = {'name': real_name}
            
        with open(JSON_DATA, 'w') as f:
            f.write(json.dumps(data))
        
        await ctx.send(content=f'Linked {discord_username} to {real_name}')
        
    @commands.command(brief="Looks up a discord account's real name and github username.")
    async def lookup(self, ctx, member=None):
        # TODO: lookup autocomplete?
        if not member:
            await ctx.send(content='Please provide a discord account to look up.')
            return
        
        try:
            with open(JSON_DATA, 'r') as f:
                data = json.load(f)
        except:
            await ctx.send(content=f'data file is broken :(')
        
        if member in data:
            user_data = data[member]
            await ctx.send(content=f'Name: {user_data["name"]}\nGithub: {user_data["github"]}')
        else:
            await ctx.send(content=f'No data found for {member}')
                
        
async def setup(bot):
    await bot.add_cog(StoreUserInfo(bot))