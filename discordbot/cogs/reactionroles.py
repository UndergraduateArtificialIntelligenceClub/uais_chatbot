import discord
import json
#import emoji
from asyncio import TimeoutError
from discord.ext import commands


class ReactionRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.roles_data = []
        self.msg_id = None
        self.settings_file = 'reactionroles.json'
        self.load_settings()

    def load_settings(self):
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
                self.msg_id = settings.get('msg_id')
                roles_data_json = settings.get('roles_data')
                self.roles_data = json.loads(roles_data_json)
        except FileNotFoundError:
            self.save_settings()

    def save_settings(self):
        settings = {
            'msg_id': self.msg_id,
            'roles_data': json.dumps(self.roles_data)
        }
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=4)

    @commands.command(brief='Creates a message with reaction roles. Call with channel ID', aliases=['rr', 'reactionroles'])
    @commands.has_permissions(administrator=True)
    async def reactionrole(self, ctx, channel_id:int=None):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            await ctx.send("Could not get channel with provided channel ID. Provide channel ID where to send the reaction message.")
            return

        if self.roles_data:
            self.roles_data = []

        # Get role reaction message content from admin
        while True:
            try:
                await ctx.send("Insert the role message you would like to send.")
                msg_input = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120)
                msg_input = msg_input.content

                # Give preview for admin to continue or redo message
                await ctx.send(f"Preview: \n\n{msg_input}\n\nType 'r' to redo message, 'c' to continue.")

                check = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120)
                check = check.content.lower()

                if check == "r":
                    await ctx.send("Redoing role message...\n")
                elif check == "c":
                    await ctx.send("Continuing...")
                    break
                else:
                    await ctx.send("Invalid input. Please try again.\n")

            except TimeoutError:
                await ctx.send("Timed out, please try again.")
                return

        # Get role emoji and role names from admin
        await ctx.send("For adding roles, input the emoji, followed by a '-', followed by the role name. An example:\n\n:smile: - Smile Role\n\n")

        while True:
            try:
                await ctx.send("Input your emoji and role name, or type 'done' if done.")
                user_input = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120)
                user_input = user_input.content

                if user_input.lower() == "done":
                    break
                elif "-" not in user_input:
                    await ctx.send("Invalid input. Be sure to include a '-' in your input. Please try again.")
                else:
                    # Split input into emoji and role name
                    emoji, role_name = user_input.split('-', 1)
                    emoji = emoji.strip()
                    emo = discord.utils.get(ctx.guild.emojis, name=emoji)
                    emo_id = emo.id
                    await ctx.send(emoji)
                    await ctx.send(emo_id)
                    role_name = role_name.strip()

                    if emoji == None:
                        await ctx.send("Invalid emoji. Please try again.")
                    else:
                        role = discord.utils.get(
                            ctx.guild.roles, name=role_name)
                        if not role:
                            role = await ctx.guild.create_role(name=role_name)

                        # Roles without new one in case user wants to redo
                        original_roles_data = self.roles_data.copy()

                        self.roles_data.append({
                            "emoji": emoji,
                            "role_name": role_name
                        })

                        # Give preview for admin to continue or redo message
                        while True:
                            await ctx.send(f"Preview:\n{emoji} = {role_name}\nType 'r' to redo, 'c' to continue.")
                            undo = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=120)
                            undo = undo.content.lower()
                            if undo == "r":
                                await ctx.send("Redoing...\n")
                                self.roles_data = original_roles_data
                                break
                            elif undo == "c":
                                await ctx.send("Continuing...")
                                break
                            else:
                                await ctx.send("Invalid input. Please try again.\n")

            except TimeoutError:
                await ctx.send("Timed out. Please try again.")
                return

        # Send reaction role message to channel
        message_content = f"{msg_input}\n"
        for role_data in self.roles_data:
            message_content += f"{role_data['emoji']} = {role_data['role_name']}\n"

        message = await channel.send(message_content)
        self.msg_id = message.id

        self.save_settings()

        for role_data in self.roles_data:
            await message.add_reaction(role_data["emoji"])
            
    # Add role upon user reaction
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)

        for roles in self.roles_data:
            if str(payload.emoji) == roles["emoji"] and payload.message_id == self.msg_id:
                role_assign = roles["role_name"]
                role = discord.utils.get(guild.roles, name=role_assign)
                await payload.member.add_roles(role, atomic=True)

    # Remove role upon user removing reaction
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        guild = self.bot.get_guild(payload.guild_id)

        for roles in self.roles_data:
            if str(payload.emoji) == roles["emoji"] and payload.message_id == self.msg_id:
                role_assign = roles["role_name"]
                role = discord.utils.get(guild.roles, name=role_assign)
                member = await guild.fetch_member(payload.user_id)
                await member.remove_roles(role, atomic=True)


async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))
