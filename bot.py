import discord
from discord.ext import commands
from credentials import TOKEN
import os,re,json, threading


#for terminal talking 
from terminal_input import start_terminal_input
ENABLE_TERMINAL = True  #ALLOW io from term
TERMINAL_CHANNEL_ID = 744962705353474140




DEBUG_BP = False

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

intents.guilds = True  #for slash commands

# Function to load the joke counter
def load_counter():
    try:
        with open(COUNTER_FILE, "r") as f:
            return json.load(f).get("counter", 0)
    except FileNotFoundError:
        return 0

# Function to save the joke counter
def save_counter(count):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"counter": count}, f)

bot = commands.Bot(command_prefix="!", intents=intents)
COUNTER_FILE = "joke_counter.json"




joke_counter = load_counter()













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


@bot.event
async def on_message(message):
    global joke_counter

    if message.author == bot.user:
        return
    text_without_urls = re.sub(r'https?:\/\/\S+', '', message.content)

    # Step 2: Find words ending with 'er' (avoiding numbers, symbols, and non-word characters)
    words = re.findall(r'\b[a-zA-Z]+er\b', text_without_urls, re.IGNORECASE)
    #Regex find ending with 'er'
    #words = re.findall(r'\b(?!https?:\/\/)[a-zA-Z]+er\b', message.content, re.IGNORECASE)

    #if they exist do jornys dumb joke
    if words:
        joke_counter += 1

        response = f"{words[0]}? I hardly know her! \n(This joke has been used **{joke_counter}** times.)"
        save_counter(joke_counter)

        #response = f"{words[0]}? I hardly know her!"
        await message.channel.send(response)

    # Process commands if there are any
    await bot.process_commands(message)


#load the cogs ( commands )
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"Loaded cog: {filename}")
            except Exception as e:
                print(f"Failed to load cog {filename}: {e}")






@bot.hybrid_command(name="spells", help="Shows a list of Cobra's available spells (commands)")
async def help_command(ctx):
    embed = discord.Embed(
        title="📜 Cobra's Spells (Help Menu)",
        description="Here are the available commands for cobra:",
        color=discord.Color.blue(),
    )

    for command in bot.commands:
        embed.add_field(name=f"/{command.name}", value=command.help, inline=False)

    embed.set_footer(text="Use / before each command to trigger a slash command.")
    
    await ctx.send(embed=embed)  


#main
async def main():
    async with bot:
        await load_cogs()

        if ENABLE_TERMINAL:
            start_terminal_input(bot, TERMINAL_CHANNEL_ID)

        await bot.start(TOKEN)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
