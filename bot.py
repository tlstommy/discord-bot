import discord
from credentials import TOKEN
from discord.ext import commands
import yt_dlp as ytdlp
import asyncio
import os
from datetime import datetime
from collections import deque
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



class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = deque()

    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.")
            return

        channel = ctx.author.voice.channel
        try:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
        except discord.errors.ClientException as e:
            await ctx.send(f"An error occurred while trying to connect: {str(e)}")

    async def leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to any voice channel.")

    async def play(self, ctx, url):
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()

        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                self.song_queue.append(player)

                if not ctx.voice_client.is_playing():
                    await self.play_next_song(ctx)
                else:
                    await ctx.send(f"**Queued:** {player.title}")

            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")
                print(f"Error occurred while trying to play: {str(e)}")

    async def play_next_song(self, ctx):
        if self.song_queue:
            current_song = self.song_queue.popleft()
            ctx.voice_client.play(current_song, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop).result())
            await ctx.send(f"**Now playing:** {current_song.title}")

    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipping current song...")

    async def pause(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to pause.")
            return

        ctx.voice_client.pause()
        await ctx.send("Paused the music.")

    async def resume(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_paused():
            await ctx.send("There's no paused music to resume.")
            return

        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")

    async def stop(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to stop.")
            return

        ctx.voice_client.stop()
        await ctx.send("Stopped the music.")

    async def show_queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is empty.")
        else:
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"**Current Queue:**\n{queue_list}")

# Instantiate the MusicPlayer class
music_player = MusicPlayer(bot)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


    activity = discord.Game(name="With Jessica")
    await bot.change_presence(status=discord.Status.online, activity=activity)


#Commands -----------------------------    

# Command: Join the voice channel
@bot.command(name='join', help="Joins the user's voice channel")
async def join(ctx):
    await music_player.join(ctx)

# Command: Leave the voice channel
@bot.command(name='leave', help="Leaves the voice channel")
async def leave(ctx):
    await music_player.leave(ctx)





#Music commands ------------------------------------------------------------------------------
# Command: Play a YouTube video/audio in the voice channel
@bot.command(name='play', help="Plays a YouTube video or audio in the voice channel")
async def play(ctx, *, url):
    await music_player.play(ctx, url)

# Command: Skip the current song
@bot.command(name='skip', help="Skips the current song")
async def skip(ctx):
    await music_player.skip(ctx)

# Command: Pause the currently playing audio
@bot.command(name='pause', help="Pauses the current audio")
async def pause(ctx):
    await music_player.pause(ctx)

# Command: Resume the paused audio
@bot.command(name='resume', help="Resumes the paused audio")
async def resume(ctx):
    await music_player.resume(ctx)

# Command: Stop the currently playing audio
@bot.command(name='stop', help="Stops the current audio")
async def stop(ctx):
    await music_player.stop(ctx)

# Command: Show the queue
@bot.command(name='queue', help="Displays the current song queue")
async def queue(ctx):
    await music_player.show_queue(ctx)




#other commands -------------------------------------------------------------------




# Command: Show user info
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
