import discord
from discord.ext import commands
from datetime import datetime
import random


from llama_cpp import Llama


llm = Llama(
    
      model_path="./models/llama-2.gguf",
      # n_gpu_layers=-1, # Uncomment to use GPU acceleration
      # seed=1337, # Uncomment to set a specific seed
      # n_ctx=2048, # Uncomment to increase the context window
)


# test llm commands 
class Ask(commands.Cog):

    



    @commands.hybrid_command(name='ask', help="ask a question")
    async def ask_llama(self, ctx, *, prompt: str):
        output = llm(
            str(f"Q:{prompt} A:"), # Prompt
            max_tokens=32, # Generate up to 32 tokens, set to None to generate up to the end of the context window
            stop=["Q:", "\n"], # Stop generating just before the model would generate a new question
            echo=True # Echo the prompt back in the output
        ) # Generate a completion, can also call create_completion
        #await ctx.send(f"{ctx.author.name} asked '{prompt}'!")
        await ctx.send(f"'{output}'!")


async def setup(bot):
    await bot.add_cog(Ask(bot))


