import discord
from credentials import TOKEN
from discord.ext import commands
import yt_dlp as ytdlp
import asyncio
import os
from datetime import datetime
import certifi

os.environ["SSL_CERT_FILE"] = certifi.where()

# Set up the bot with the correct intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

# yt-dlp options
ytdlp_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',  # Allows for searching if no full URL is provided
}

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',  # Skip video, only audio
}

ytdlp_extractor = ytdlp.YoutubeDL(ytdlp_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdlp_extractor.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]  # Take the first item from a playlist if available

        filename = data['url'] if stream else ytdlp_extractor.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Command: Join the voice channel
@bot.command(name='join', help="Joins the user's voice channel")
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.")
        return

    channel = ctx.author.voice.channel

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

# Command: Leave the voice channel
@bot.command(name='leave', help="Leaves the voice channel")
async def leave(ctx):
    if ctx.voice_client is not None:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not connected to any voice channel.")

# Command: Play a YouTube video/audio in the voice channel
@bot.command(name='play', help="Plays a YouTube video or audio in the voice channel")
async def play(ctx, *, url):
    if ctx.voice_client is None:
        await  ctx.author.voice.channel.connect()
        

    async with ctx.typing():
        try:
            player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
            ctx.voice_client.stop()  # Stop any currently playing music before playing a new track
            ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
            await ctx.send(f"**Now playing:** {player.title}")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            print(f"Error occurred while trying to play: {str(e)}")

# Command: Pause the currently playing audio
@bot.command(name='pause', help="Pauses the current audio")
async def pause(ctx):
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        await ctx.send("There's no music playing to pause.")
        return

    ctx.voice_client.pause()
    await ctx.send("Paused the music.")

# Command: Resume the paused audio
@bot.command(name='resume', help="Resumes the paused audio")
async def resume(ctx):
    if ctx.voice_client is None or not ctx.voice_client.is_paused():
        await ctx.send("There's no paused music to resume.")
        return

    ctx.voice_client.resume()
    await ctx.send("Resumed the music.")

# Command: Stop the currently playing audio
@bot.command(name='stop', help="Stops the current audio")
async def stop(ctx):
    if ctx.voice_client is None or not ctx.voice_client.is_playing():
        await ctx.send("There's no music playing to stop.")
        return

    ctx.voice_client.stop()
    await ctx.send("Stopped the music.")


# Command: Check if bot is in the voice channel
@bot.command(name='current', help="Displays the current voice channel status")
async def current(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await ctx.send(f"I'm currently connected to {voice.channel}.")
    else:
        await ctx.send("I'm not connected to any voice channel.")


@bot.command(name='userinfo', help="Displays information about the user")
async def userinfo(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author  # If no user is mentioned, get info for the message author

    roles = [role.mention for role in member.roles[1:]]  # Skip @everyone role
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
    






# Run the bot
bot.run(TOKEN)
