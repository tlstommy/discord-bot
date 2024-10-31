import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from collections import deque
from utils import YTDLSource #settings for ytdl

import concurrent.futures
download_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2) 

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = deque()


    #plays a vid
    @commands.hybrid_command(name='play', help="Plays a YouTube video or audio in the voice channel")
    async def play(self, ctx, *, url: str):
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.",ephemeral=True)
            return
        if ctx.voice_client is None:
            await ctx.author.voice.channel.connect()


        #download vid in a new thread to not lag
        async with ctx.typing():
            try:
                player = await YTDLSource.from_url(url, stream=True)
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
            
            embed = discord.Embed(
                title=f"Now Playing",
                color=discord.Color.green(),
                url=current_song.link_url,
            )



            embed.set_thumbnail(url=current_song.thumbnail)
            embed.add_field(name=current_song.title, value=current_song.uploader)
            embed.add_field(name="Length", value=current_song.length)
            view = ControlView(ctx)
            await ctx.send(embed=embed,view=view)


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
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to stop.",ephemeral=True)
            return
        
        ctx.voice_client.stop()
        self.song_queue = deque()
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped the music.")


    #prints thd deque
    @commands.hybrid_command(name='queue', help="Displays the current song queue")
    async def queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is empty.")
        else:
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"**Current Queue:**\n{queue_list}",ephemeral=True)

#buttons 
class ControlView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx


    #leave vc 
    @discord.ui.button(label="☒", style=discord.ButtonStyle.secondary)
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
    @discord.ui.button(label="⪭", style=discord.ButtonStyle.secondary)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            await interaction.response.send_message(f"{self.ctx.author.name} skipped the song.")


    



#load the cog into the bot
async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
