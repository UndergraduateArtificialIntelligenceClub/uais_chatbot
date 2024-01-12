import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

class AuditLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def is_admin_or_executive_check(ctx):
        # Check if the user is an admin
        if ctx.author.guild_permissions.administrator:
            return True

        # Check if the user has the 'executive' role
        return any(role.name.lower() == 'executive' for role in ctx.author.roles)

    @commands.command(name='printlogs', aliases=['PrintLogs'])
    @commands.check(is_admin_or_executive_check)
    async def print_logs(self, ctx, user: discord.User = None, limit: int = 10):
        # call with !printlogs @Username <Number of logs to print>
        # Example: !printlogs @John 5
        if user is None:
            await ctx.send("Usage: `!printlogs @Username [Num Logs to Print]`\nExample: `!printlogs @John 5`")
            return
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
        except Exception:
            await ctx.send("Something went horribly wrong")
            
    def _format_action(self, action):
    # Extract the name of the action from AuditLogAction
        if isinstance(action, discord.AuditLogAction):
            return action.name
        else:
            return str(action)
    
    def _format_target(self, target):
        # Format the target based on its type
        if isinstance(target, discord.User) or isinstance(target, discord.Member):
            return f'User: {target.name}#{target.discriminator}'
        elif isinstance(target, discord.Role):
            return f'Role: {target.name}'
        elif isinstance(target, discord.TextChannel):
            return f'Text Channel: #{target.name}'
        elif isinstance(target, discord.VoiceChannel):
            return f'Voice Channel: {target.name}'
        elif isinstance(target, discord.CategoryChannel):
            return f'Category: {target.name}'
        elif isinstance(target, discord.StageChannel):
            return f'Stage Channel: {target.name}'
        elif isinstance(target, discord.Emoji):
            return f'Emoji: {target.name}'
        elif isinstance(target, discord.Sticker):
            return f'Sticker: {target.name}'
        elif isinstance(target, discord.Invite):
            return f'Invite: {target.url}'
        elif isinstance(target, discord.ScheduledEvent):
            return f'Scheduled Event: {target.name}'
        elif isinstance(target, discord.Integration):
            return f'Integration: {target.name}'
        elif isinstance(target, discord.PartialIntegration):
            name = getattr(target, 'name')
            return f'Partial Integration: {name}'
        elif isinstance(target, discord.PermissionOverwrite):
            return f'Permission Overwrite: {target.id}'
        else:
            target_id = getattr(target, 'id', 'Unknown ID')
            target_type = type(target).__name__
            return f'Object: {target_type} (ID: {target_id})'
    
    async def cog_command_error(self, ctx, error):
        # Check if the error is due to missing required role/permissions
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You must be an admin or an executive to use this command.")
        else:
            # Other errors
            print(f"An error occurred: {error}")


async def setup(bot):
    await bot.add_cog(AuditLog(bot))