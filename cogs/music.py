import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from collections import deque
from utils import YTDLSource #settings for ytdl
from random import shuffle
import os
import shutil

import concurrent.futures
download_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2) 

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = deque()


    #plays a vid
    @commands.hybrid_command(name='play', help="Plays a YouTube video or audio in the voice channel")
    async def play(self, ctx, *, url: str):
        print("play command called")
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.",ephemeral=True)
            return
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()


        #download vid in a new thread to not lag
        async with ctx.typing():
            print("preparing to extract")
            try:
                player = await YTDLSource.from_url(url, stream=False)
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
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            return

        if self.song_queue:
            current_song = self.song_queue.popleft()
            filename = None
            if hasattr(current_song, 'data') and not current_song.data.get('is_live', False):
                filename = current_song.data.get('_filename')

            def after_playback(error):
                # Clean up file
                if filename and os.path.exists(filename):
                    try:
                        os.remove(filename)
                    except Exception as e:
                        print(f"Error deleting file: {e}")
                # Only call play_next_song if there are more songs
                fut = asyncio.run_coroutine_threadsafe(self.play_next_song(ctx), self.bot.loop)
                try:
                    fut.result()
                except Exception as e:
                    print(f"Error in after callback: {e}")

            ctx.voice_client.play(current_song, after=after_playback)

            embed = discord.Embed(
                title=f"Now Playing",
                color=discord.Color.green(),
                url=current_song.link_url,
            )
            embed.add_field(name="Title", value=current_song.title)
            await ctx.send(embed=embed)
        else:
            await asyncio.sleep(10)
            if ctx.voice_client and not ctx.voice_client.is_playing():
                await ctx.voice_client.disconnect()
                clear_downloads()


    #skips the song
    @commands.hybrid_command(name='skip', help="Skips the current song")
    async def skip(self, ctx):
        if ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("Skipping current song...")

    #pause the song
    @commands.hybrid_command(name='pause', help="Pauses the current audio")
    async def pause(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to pause.",ephemeral=True)
            return

        ctx.voice_client.pause()
        await ctx.send("Paused the music.")

    #unpause
    @commands.hybrid_command(name='resume', help="Resumes the paused audio")
    async def resume(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_paused():
            await ctx.send("There's no paused music to resume.",ephemeral=True)
            return

        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")


    #stop the song
    @commands.hybrid_command(name='stop', help="Stops the current audio")
    async def stop(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.",ephemeral=True)
            return
        
        ctx.voice_client.stop()
        self.song_queue = deque()
        await ctx.voice_client.disconnect()
        clear_downloads()
        await ctx.send("Stopped the music.")


    #prints thd deque
    @commands.hybrid_command(name='queue', help="Displays the current song queue")
    async def queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is empty.")
        else:
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"**Current Queue:**\n{queue_list}",ephemeral=True)

    #shuffle the queue
    @commands.hybrid_command(name='shuffle', help="Shuffles the queue")
    async def shuffle_queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is empty.")
        else:
            shuffle(self.song_queue)
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"**Shuffled Queue!**\n")


#buttons 
class ControlView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx


    #leave vc 
    @discord.ui.button(label="✕", style=discord.ButtonStyle.secondary)
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            self.song_queue = deque()
            await self.ctx.voice_client.disconnect()
            await interaction.response.send_message("Stopped the song and left the VC.", ephemeral=True)

    # Play/Pause button
    @discord.ui.button(label="||", style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        #if playing  pause
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.pause()
            button.label = "▷"  # Change the button label to Resume
            await interaction.response.edit_message(content="Audio Paused.", view=self)
        #else unpause
        elif self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            button.label = "||"  # Change the button label back to Pause
            await interaction.response.edit_message(content="Audio Playing.", view=self)

    #skip button
    @discord.ui.button(label="≥", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            await interaction.response.send_message(f"{self.ctx.author.name} skipped the song.")

    #shuffle button
    @discord.ui.button(label="⤨", style=discord.ButtonStyle.secondary)
    async def shuffle_button(self, interaction: discord.Interaction, button: Button):
        shuffle_command = self.ctx.bot.get_command("shuffle")
        await self.ctx.invoke(shuffle_command)


def clear_downloads():
    folder = "downloads"
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

#load the cog into the bot
async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
