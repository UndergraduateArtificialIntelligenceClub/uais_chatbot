import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

class AuditLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='printlogs')
    @commands.has_permissions(administrator=True)
    async def print_logs(self, ctx, user: discord.User):
        try:
            # Fetch the audit logs for the server
            logs = []
            async for log in ctx.guild.audit_logs(limit=10, user=user):
                logs.append(log)

            # Create a string with the audit log information
            log_info = "\n\n".join([f"{log.user} did {log.action} to {log.target}" for log in logs])

            # Send the audit log information to the channel
            if len(logs)!=0:
                await ctx.send(f'Audit Log History:\n{log_info}')
            else:
                await ctx.send(content="This user has no audit history")

        except discord.Forbidden:
            await ctx.send("I don't have permission to access the audit logs.")
        except commands.CheckFailure:
            await ctx.send("You must be an admin to use this command")

async def setup(bot):
    await bot.add_cog(AuditLog(bot))