import discord
from discord.ext import commands
from datetime import datetime

class UserInfo(commands.Cog):
    @commands.hybrid_command(name='userinfo', help="Displays information about the user")
    async def userinfo(self, ctx, *, member: discord.Member = None):
        if member is None:
            member = ctx.author  #if no user is mentioned, get info for the message author

        roles = [role.mention for role in member.roles[1:]]  #ignore @everyone role
        embed = discord.Embed(
            title=f"User Info - {member}",
            color=discord.Color.green(),
            timestamp=datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="ID", value=member.id)
        embed.add_field(name="Display Name", value=member.display_name)
        embed.add_field(name="Created At", value=member.created_at.strftime("%b %d, %Y"))
        embed.add_field(name="Joined Server", value=member.joined_at.strftime("%b %d, %Y"))
        embed.add_field(name="Roles", value=",".join(roles))

        await ctx.send(embed=embed)

# Load the cog into the bot
async def setup(bot):
    await bot.add_cog(UserInfo(bot))
