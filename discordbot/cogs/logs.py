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
    async def print_logs(self, ctx, user: discord.User, limit: int = 10):
        try:
            # Fetch the audit logs for the server
            logs = []
            async for log in ctx.guild.audit_logs(limit=limit, user=user):
                logs.append(log)

            # Create a string with the audit log information
            printable_logs = ""
            for log in logs:
                printable_logs += f"{log.user} did {self._format_action(log.action)} to {self._format_target(log.target)}\n\n"

            # Send the audit log information to the channel
            if len(logs)!=0:
                await ctx.send(f'Audit Log History:\n{printable_logs}')
            else:
                await ctx.send(content="This user has no audit history")

        except discord.Forbidden:
            await ctx.send("I don't have permission to access the audit logs.")
        except commands.CheckFailure:
            await ctx.send("You must be an admin to use this command")
            
    def _format_action(self, action):
    # Extract the name of the action from AuditLogAction
        if isinstance(action, discord.AuditLogAction):
            return action.name
        else:
            return str(action)
    
    def _format_target(self, target):
        # Format the target based on its type
        if isinstance(target, discord.User):
            return f'user: {target.name}'
        elif isinstance(target, discord.Role):
            return f'role: {target.name}'
        elif isinstance(target, discord.TextChannel):
            return f'text Channel: #{target.name}'
        elif isinstance(target, discord.VoiceChannel):
            return f'voice Channel: {target.name}'
        else:
            return str(target)

async def setup(bot):
    await bot.add_cog(AuditLog(bot))