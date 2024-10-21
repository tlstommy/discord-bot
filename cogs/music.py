import discord
from discord.ext import commands
from discord.ui import Button, View
import asyncio
from collections import deque
from utils import YTDLSource #settings for ytdl

class MusicPlayer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = deque()


    #plays a vid
    @commands.hybrid_command(name='play', help="Plays a YouTube video or audio in the voice channel")
    async def play(self, ctx, *, url: str):
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
            
            embed = discord.Embed(
                title=f"Now Playing",
                color=discord.Color.green(),
                url=current_song.link_url,
            )


            button1 = Button(
                style=discord.ButtonStyle.primary,
                custom_id="button1",
                label="test",
            )
            button2 = Button(
                style=discord.ButtonStyle.secondary,
                custom_id="button2",
                label="test",
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
            await ctx.send("There's no music playing to pause.")
            return

        ctx.voice_client.pause()
        await ctx.send("Paused the music.")

    #unpause
    @commands.hybrid_command(name='resume', help="Resumes the paused audio")
    async def resume(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_paused():
            await ctx.send("There's no paused music to resume.")
            return

        ctx.voice_client.resume()
        await ctx.send("Resumed the music.")


    #stop the song
    @commands.hybrid_command(name='stop', help="Stops the current audio")
    async def stop(self, ctx):
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("There's no music playing to stop.")
            return

        ctx.voice_client.stop()
        await ctx.send("Stopped the music.")


    #prints thd deque
    @commands.hybrid_command(name='queue', help="Displays the current song queue")
    async def queue(self, ctx):
        if not self.song_queue:
            await ctx.send("The song queue is empty.")
        else:
            queue_list = "\n".join([f"{i+1}. {song.title}" for i, song in enumerate(self.song_queue)])
            await ctx.send(f"**Current Queue:**\n{queue_list}")

# View to hold the buttons (controls for the music)
class ControlView(View):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx

    #skip button
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary)
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.stop()
            await interaction.response.send_message("Skipped the song.", ephemeral=True)

    # Play/Pause button
    @discord.ui.button(label="Pause", style=discord.ButtonStyle.secondary)
    async def pause_button(self, interaction: discord.Interaction, button: Button):
        # If music is playing, pause it and change the button label to "Resume"
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.pause()
            button.label = "Resume"  # Change the button label to Resume
            await interaction.response.edit_message(content="Paused.", view=self)
        # If music is paused, resume it and change the button label to "Pause"
        elif self.ctx.voice_client.is_paused():
            self.ctx.voice_client.resume()
            button.label = "Pause"  # Change the button label back to Pause
            await interaction.response.edit_message(content="Resumed.", view=self)


    



#load the cog into the bot
async def setup(bot):
    await bot.add_cog(MusicPlayer(bot))
