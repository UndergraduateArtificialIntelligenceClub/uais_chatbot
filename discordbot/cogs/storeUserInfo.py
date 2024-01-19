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
        
        with open(JSON_DATA, 'r') as f:
            data = json.load(f)
        
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
        
        with open(JSON_DATA, 'r') as f:
            data = json.load(f)
            
        if discord_username in data:
            data[discord_username]['name'] = real_name
        else:
            data[discord_username] = {'name': real_name}
            
        with open(JSON_DATA, 'w') as f:
            f.write(json.dumps(data))
        
        await ctx.send(content=f'Linked {discord_username} to {real_name}')
        
    @commands.command(brief="Looks up a discord account's real name and github username.")
    async def lookupname(self, ctx, discord=None):
        if not discord:
            await ctx.send(content='Please provide a discord account to look up.')
            return
        await ctx.send(content='hi')
        
        
async def setup(bot):
    await bot.add_cog(StoreUserInfo(bot))