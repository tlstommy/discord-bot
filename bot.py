import discord
from discord.ext import commands
from credentials import TOKEN
import os

DEBUG_BP = False

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

intents.guilds = True  #for slash commands


bot = commands.Bot(command_prefix="!", intents=intents)

#bot inits
@bot.event
async def on_ready():
    
    

    

    try:
        synced = await bot.tree.sync()  #syncs all the global slash commands
        print(f"Synced {len(synced)} global commands")
    except Exception as e:
        print(f"Failed to sync global commands: {e}")
    
    
    
    
    
    
    
    #set status
    activity = discord.Activity(type=discord.ActivityType.listening, name="Ozzy")

    #bring online
    await bot.change_presence(status=discord.Status.online, activity=activity)
    

    


    #bot ready
    print(f'Logged in as {bot.user.name}')

#load the cogs ( commands )
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")

#main
async def main():
    async with bot:
        await load_cogs() 
        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
