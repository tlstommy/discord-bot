import discord
from discord.ext import commands
from datetime import datetime
import random,os,time
import asyncio
from datetime import timedelta


#'fun' commands - ones that are just kinda misc/for fun
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
       

    @commands.hybrid_command(name='rtd', help="roles a n-sided die")
    async def dice_role(self, ctx, *, sides: int = 6):
        die = random.randint(1,abs(sides))
        await ctx.send(f"{ctx.author} rolled a {die}!")
    
    @commands.hybrid_command(name='ping', help="pong")
    async def ping(self, ctx):
        print("ping called")
        
        latency_ms = round(self.bot.latency * 1000) 
        
        await ctx.send(f"Pong! ({latency_ms}ms)",ephemeral=True)
    
    @commands.hybrid_command(name="duel", help="Challenge a user to a duel!")
    async def duel(self, ctx, opponent: discord.Member):    

        if opponent == ctx.author:
            await ctx.send("You can't duel yourself!")
            return
        if opponent.bot:
            await ctx.send("You can't duel a bot!")
            return

        #send duel request
        duel_message = await ctx.send(f"{opponent.mention}, {ctx.author.mention} has challenged you to a duel! Do you accept?")

        await duel_message.add_reaction("✅")  # Accept
        await duel_message.add_reaction("❌")  # Decline

        def check(reaction, user):
            return user == opponent and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == duel_message.id

        try:
            reaction, user = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(f"{opponent.mention} did not respond in time.")
            return

        if str(reaction.emoji) == "❌":
            await ctx.send(f"{opponent.mention} declined the duel.")
            return
        await duel_message.delete()
        # Duel accepted, determine the winner
        await ctx.send(f"{opponent.mention} accepted the duel! The duel begins...")

        await asyncio.sleep(3)
        

        countdown_message = await ctx.send("3...")
        await asyncio.sleep(2)
        for i in range(2, 0, -1):
            await countdown_message.delete()
            countdown_message = await ctx.send(f"{i}...")
            await asyncio.sleep(2)
         
        await countdown_message.edit(content="Duel!\n")
        winner, loser = (ctx.author, opponent) if random.choice([True, False]) else (opponent, ctx.author)

        await ctx.send(f"😎 **{winner.mention} wins the duel!**")
        await ctx.send(f"🤣🫵  **{loser.mention} is a loser! haha!!**")
        await asyncio.sleep(2)
        #kick tyhe loser
        try:
            await loser.move_to(None)
           
        except discord.Forbidden as e:
            print(e)
            
   


async def setup(bot):
    await bot.add_cog(Fun(bot))


