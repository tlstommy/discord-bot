import discord
from discord.ext import commands
from datetime import datetime
import random,os,time
import asyncio
from datetime import timedelta
import aiohttp

#'fun' commands - ones that are just kinda misc/for fun
class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
       

    @commands.hybrid_command(name='rtd', help="Roles a n-sided die")
    async def dice_role(self, ctx, *, sides: int = 6):
        die = random.randint(1,abs(sides))
        await ctx.send(f"{ctx.author} rolled a {die}!")
    
    @commands.hybrid_command(name='ping', help="Pong")
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
            #return user == user and str(reaction.emoji) in ["✅", "❌"] and reaction.message.id == duel_message.id

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


    @commands.hybrid_command(name="coinflip", help="Flips a coin")
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"🪙 {ctx.author.mention}, the coin landed on **{result}**!")

    @commands.hybrid_command(name="8ball", help="Ask the magic 8-ball a question")
    async def eight_ball(self, ctx, *, question: str):
        responses = [
            "It is certain.",
            "Without a doubt.",
            "You may rely on it.",
            "Yes, definitely.",
            "Ask again later.",
            "Better not tell you now.",
            "Don't count on it.",
            "My reply is no.",
            "Very doubtful."
        ]
        answer = random.choice(responses)
        await ctx.send(f"🎱 {ctx.author.mention}, you asked: *{question}*\n**Answer:** {answer}")

    @commands.hybrid_command(name="choose", help="Let cobra decide for you")
    async def choose(self, ctx, choices: str):
        options = choices.split(",")
        if len(options) < 2:
            await ctx.send("You need to provide at least two options separated by commas!")
        else:
            decision = random.choice(options).strip()
            await ctx.send(f"{ctx.author.mention}, I choose: **{decision}**! TWU")
        
   

    @commands.hybrid_command(name="meme", help="Cobra shows you a meme from his personal collection")
    async def meme(self,ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.com/gimme") as resp:
                data = await resp.json()
                await ctx.send(data["url"])

    @commands.hybrid_command(name="roast", help="Roasts a sicko")
    async def roast(self, ctx, victim: discord.Member):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://evilinsult.com/generate_insult.php?lang=en&type=json") as resp:

                data = await resp.json()
                insult = data.get("insult")
                
                await ctx.send(f"🔥 {victim.mention}, {data['insult']}")


    @commands.hybrid_command(name="cobrafact", help="Cobra blesses you with knowledge from his gothic wisdom")
    async def fact(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://uselessfacts.jsph.pl/random.json?language=en") as resp:
                data = await resp.json()
                await ctx.send(f"**Did you know?**\n {data['text']}\n")

    @commands.hybrid_command(name="cobrajoke", help="Cobra tells a joke")
    async def dadjoke(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json"}) as resp:
                data = await resp.json()
                await ctx.send(f"{data['joke']}")


    @commands.hybrid_command(name="cobrapussy", help="Cobra shows you a picture of his pussy")
    async def cat(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                data = await resp.json()
                await ctx.send(data[0]["url"])


async def setup(bot):
    await bot.add_cog(Fun(bot))


