import discord
from discord.ext import commands
from datetime import datetime
import asyncio


class Management(commands.Cog):
    @commands.hybrid_command(name='rename', help="Renames the bot.")
    @commands.has_permissions(administrator=True)#only admins can do this
    async def rename(self, ctx, *, name: str):
        if ctx.author.guild_permissions.administrator:
            await ctx.guild.me.edit(nick=name)
            await ctx.send(f"Nickname changed to: {name}")
        else:
            await ctx.send(f"You must be an admin to run this command.",ephemeral=True) 


    @commands.hybrid_command(name="say", description="Cobes will speak his mind")
    #@commands.has_permissions(administrator=True)#only admins can do this
    async def say(self, ctx, *, message: str):

        
        
        # Send the response as visible to everyone
        messageTest = await ctx.send(f"{message}", tts=True)
        await asyncio.sleep(5)
        await messageTest.delete()

        # Let the command execution remain private (ephemeral)
        await ctx.respond("Command executed successfully.", ephemeral=True)

    


# Load the cog into the bot
async def setup(bot):
    await bot.add_cog(Management(bot))
