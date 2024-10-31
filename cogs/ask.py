import discord
from discord.ext import commands
from datetime import datetime
import random,json




# test llm commands 
class Ask(commands.Cog):

    



    @commands.hybrid_command(name='ask', help="ask a question")
    async def ask_llama(self, ctx, *, prompt: str):

        
        await ctx.send("disabled toobz :(",ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ask(bot))


