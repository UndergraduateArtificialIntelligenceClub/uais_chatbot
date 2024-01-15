
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.reactions = True

# Command to make role message
class RoleCommand(commands.Cog):
    message_id = None

    def __init__(self, bot):
        self.bot = bot
        self.roles_data = []
        self.msg_id = None

    @commands.command(brief='gets user to add a role assignment message', aliases=['rr'])
    @commands.has_permissions(administrator=True)
    async def reactionrole(self, ctx):
        if self.roles_data != []:
            self.roles_data = []
            
        #Get channel id 
        await ctx.send("Copy and paste the channel ID of the channel you would like to send your reaction message to.")
        channel_id = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        channel_id = int(channel_id.content)

        channel = self.bot.get_channel(channel_id)
        if not channel:
            return await ctx.send("Invalid channel. Please try again.")

         #Get role reaction message content
        await ctx.send("Insert the role message you would like to send.")
        msg_input = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
        msg_input = msg_input.content

        #Get role emoji and role names
        await ctx.send("Now we input the role emoji and role names. You will be asked to input an emoji for users to react to, following the role name to use/create. When finished, type 'done'.")

        while True:
            await ctx.send("Input emoji or type 'done' if done:")
            emoji_input = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            emoji_input = emoji_input.content

            if emoji_input.lower() == 'done':
                break

            await ctx.send("Input role name:")
            role_name_input = await self.bot.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel)
            role_name_input = role_name_input.content

            role = discord.utils.get(ctx.guild.roles, name=role_name_input)
            if not role:
                try:
                    role = await ctx.guild.create_role(name=role_name_input)
                except discord.Forbidden:
                    return await ctx.send("I don't have the permissions to create roles.")

            self.roles_data.append({
                "emoji": emoji_input,
                "role_name": role_name_input
             })

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
    #await bot.add_cog(ReactionRoleAssign(bot))
    await bot.add_cog(RoleCommand(bot))


