import discord
import asyncio
from discord.ext import commands


class ReactionRoles(commands.Cog):
    message_id = None

    def __init__(self, bot):
        self.bot = bot
        self.roles_data = []
        self.msg_id = None

    @commands.command(brief='gets user to add a role assignment message', aliases=['rr', 'reactionroles'])
    @commands.has_permissions(administrator=True)
    async def reactionrole(self, ctx):
        if self.roles_data != []:
            self.roles_data = []

        # Get channel ID from admin
        await ctx.send("Copy and paste the channel ID of the channel you would like to send your reaction message to.")
   
        try:
            channel_id = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
            channel_id = int(channel_id.content)
            channel = discord.utils.get(ctx.guild.channels, id=channel_id)

            if channel == None:
                await ctx.send("Invalid channel ID. Please try again.")
                return
            
        except asyncio.TimeoutError:
            await ctx.send("Timed out. Command will exit now.")
            return
        
        channel = self.bot.get_channel(channel_id)

        # Get role reaction message content from admin
        while True:
            try:
                await ctx.send("Insert the role message you would like to send.")
                msg_input = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
                msg_input = msg_input.content

                # Give preview for admin to continue or redo message
                await ctx.send(f"Preview: \n\n{msg_input}\n\nType 'r' to redo message, 'c' to continue.")

                check = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=30)
                check = check.content.lower()

                if check == "r":
                    await ctx.send("Redoing role message...\n")
                elif check == "c":
                    await ctx.send("Continuing...")
                    break
                else:
                    await ctx.send("Invalid input. Please try again.\n")

            except asyncio.TimeoutError:
                await ctx.send("Timed out. Please try again.")
                return

        # Get role emoji and role names from admin
        await ctx.send("For adding roles, input the emoji, followed by a '-', followed by the role name. An example:\n\n:smile: - Smile Role\n\n")

        while True:
            try:
                await ctx.send("Input your emoji and role name, or type 'done' if done.")
                user_input = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
                user_input = user_input.content

                if user_input.lower() == "done":
                    break
                elif "-" not in user_input:
                    await ctx.send("Invalid input. Be sure to include a '-' in your input. Please try again.")
                else:
                    # Split input into emoji and role name
                    emoji, role_name = user_input.split('-', 1)
                    emoji = emoji.strip()
                    role_name = role_name.strip()

                    if emoji == None:
                        await ctx.send("Invalid emoji. Please try again.")
                    else:
                        role = discord.utils.get(ctx.guild.roles, name=role_name)
                        if not role:
                            role = await ctx.guild.create_role(name=role_name)
                        
                        original_roles_data = self.roles_data.copy() # Roles without new one in case user wants to redo

                        self.roles_data.append({
                            "emoji": emoji,
                            "role_name": role_name
                        })

                        # Give preview for admin to continue or redo message
                        while True:
                            await ctx.send(f"Preview:\n{emoji} = {role_name}\nType 'r' to redo, 'c' to continue.")
                            undo = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=60)
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

            except asyncio.TimeoutError:
                await ctx.send("Timed out. Please try again.")
                return

        # Send reaction role message to channel
        message_content = f"{msg_input}\n"
        for role_data in self.roles_data:
            message_content += f"{role_data['emoji']} = {role_data['role_name']}\n"

        message = await channel.send(message_content)
        self.msg_id = message.id

        for role_data in self.roles_data:
            await message.add_reaction(role_data["emoji"])

        self.bot.reaction_roles.setdefault(ctx.guild.id, []).extend([{"message_id": message.id, **role_data} for role_data in self.roles_data])
    
    #Add role upon user reaction
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
                    

    #Remove role upon user reaction
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
