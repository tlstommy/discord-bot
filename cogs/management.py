import discord
from discord.ext import commands
from datetime import datetime


class Management(commands.Cog):
    @commands.hybrid_command(name='rename', help="Renames the bot.")
    @commands.has_permissions(administrator=True)#only admins can do this
    async def rename(self, ctx, *, name: str):
        if ctx.author.guild_permissions.administrator:
            await ctx.guild.me.edit(nick=name)
            await ctx.send(f"Nickname changed to: {name}")
        else:
            await ctx.send(f"You must be an admin to run this command.",ephemeral=True) 

# Load the cog into the bot
async def setup(bot):
    await bot.add_cog(Management(bot))
