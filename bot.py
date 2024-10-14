import discord
from credentials import TOKEN
from discord.ext import commands

import asyncio
import os

import certifi

import yt_dlp as ytdlp
import asyncio

os.environ["SSL_CERT_FILE"] = certifi.where()


# Set up the bot with the right intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
bot = commands.Bot(command_prefix="!", intents=intents)

#loadup opus
discord.opus.load_opus("opus")
discord.opus.load_opus()


# yt-dlp options
ytdlp_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
}



ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
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
            # Take the first item from a playlist if provided
            data = data['entries'][0]

        filename = data['url'] if stream else ytdlp_extractor.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.event
async def on_ready():
    print(f'Logged in as bot tars')

# Commands for the bot
@bot.command(name='join', help="Joins the voice channel")
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel.")
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name='leave', help="Leaves the voice channel")
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='play', help="Plays a YouTube video in the voice channel")
async def play(ctx, url):
    
    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        voice_channel.play(player, after=lambda e: print(f'Player error: {e}') if e else None)
        print(f"Now playing: {player.title}")  # Add this for debugging
        
    



    await ctx.send(f"**Now playing:** {player.title}")
    


@bot.command(name='pause', help="Pauses the current song")
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
        await ctx.send("Music paused.")
    else:
        await ctx.send("No music is currently playing.")


@bot.command(name='resume', help="Resumes the current song")
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
        await ctx.send("Music resumed.")
    else:
        await ctx.send("The music is not paused.")


@bot.command(name='stop', help="Stops the current song")
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Music stopped.")
    else:
        await ctx.send("No music is currently playing.")


# Run the bot
bot.run(TOKEN)
