import discord
from discord.ext import commands
import asyncio
from collections import deque
from utils import YTDLSource #settings for ytdl

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = deque()


    #plays a vid
    @commands.command(name='play', help="Plays a YouTube video or audio in the voice channel")
    async def play(self, ctx, *, url):
        print("Play called!!")
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.")
            return
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

    #plays the next song
    async def play_next_song(self, ctx):
        if self.song_queue:
            current_song = self.song_queue.popleft()
            ctx.voice_client.play(current_song, after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop).result())
            await ctx.send(f"**Now playing:** {current_song.title}")


    #skips the song
    @commands.command(name='skip', help="Skips the current song")
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipping current song...")

    #pause the song
    @commands.command(name='pause', help="Pauses the current audio")
    async def pause(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to pause.")
            return

        ctx.voice_client.pause()
        await ctx.send("Paused the music.")

    #unpause
    @commands.command(name='resume', help="Resumes the paused audio")
    async def resume(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_paused():
            await ctx.send("There's no paused music to resume.")
            return

        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")


    #sop the song
    @commands.command(name='stop', help="Stops the current audio")
    async def stop(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to stop.")
            return

        ctx.voice_client.stop()
        await ctx.send("Stopped the music.")


    #prints thd deque
    @commands.command(name='queue', help="Displays the current song queue")
    async def queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is empty.")
        else:
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"**Current Queue:**\n{queue_list}")

#load the cog into the bot
async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
