import os
import pathlib
import json
from discord.ext import commands
from Secret import TOKEN

os.chdir(pathlib.Path(__file__).parent.absolute())
with open("jsons/settings.json", "r") as f:
    settings = json.load(f)

client = commands.Bot(command_prefix=settings["BOT_PREFIX"])


@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')
    await ctx.message.delete(delay=1)


@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')
    await ctx.message.delete(delay=1)


@client.command()
async def reload(ctx, extension):
    client.reload_extension(f'cogs.{extension}')
    await ctx.message.delete(delay=1)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(TOKEN)
