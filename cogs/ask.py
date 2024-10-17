import discord
from discord.ext import commands
from datetime import datetime
import random


from llama_cpp import Llama


llm = Llama(
    
      model_path="./models/dolphin-2.2.1.gguf",
      #model_path="./models/mistral-7b-instruct-v0.2.Q4_K_M.gguf"
      # n_gpu_layers=-1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)


# test llm commands 
class Ask(commands.Cog):

    



    @commands.hybrid_command(name='ask', help="ask a question")
    async def ask_llama(self, ctx, *, prompt: str):

        

        output = llm(str(f"Q: {prompt} A:"),max_tokens=None,temperature=0.9,top_p=0.7,stop=["Q:", "\n"], echo=False) 
        #await ctx.send(f"{ctx.author.name} asked '{prompt}'!")
        print(output['choices'][0].get('text'))
        print(output)
        embed = discord.Embed(
            title=f"{prompt}",
            color=discord.Color.green(),
        )
        embed.add_field(name="", value=output['choices'][0].get('text'))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Ask(bot))


