import discord
from discord.ext import commands

class VoiceManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='join', help="Joins the user's voice channel")
    async def join(self, ctx):
        if not ctx.author.voice:
            await ctx.send(f"{ctx.author.name}, you need to join a voice channel first.",ephemeral=True)
            return

        channel = ctx.author.voice.channel
        try:
            if ctx.voice_client is not None:
                await ctx.voice_client.move_to(channel)
            else:
                await channel.connect()
        except discord.errors.ClientException as e:
            await ctx.send(f"An error occurred while trying to connect: {str(e)}")

    @commands.hybrid_command(name='leave', help="Leaves the voice channel")
    async def leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()
            await ctx.send("Disconnected from the voice channel.")
        else:
            await ctx.send("I'm not connected to any voice channel.",ephemeral=True)

#load the cog into the bot
async def setup(bot):
    await bot.add_cog(VoiceManagement(bot))
