import discord
from discord.ext import commands
from datetime import datetime
import random,time


#'fun' commands - ones that are just kinda misc/for fun
class Fun(commands.Cog):
    @commands.hybrid_command(name='rtd', help="roles a n-sided die")
    async def dice_role(self, ctx, *, sides: int = 6):
        die = random.randint(1,abs(sides))
        await ctx.send(f"{ctx.author.name} rolled a {die}!")
    
    @commands.hybrid_command(name='ping', help="pong")
    async def ping(self, ctx):
        await ctx.send(f"pong!")


async def setup(bot):
    await bot.add_cog(Fun(bot))


