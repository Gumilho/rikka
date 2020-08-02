import json
import discord
from discord.ext import commands

with open("jsons/settings.json", "r") as f:
    settings = json.load(f)


def is_admin():
    async def predicate(ctx):
        return any(filter(lambda role: role.name == "Admin", ctx.author.roles))

    return commands.check(predicate)


class CustomReactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reactions = {}

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_images()
        print("Loaded CustomReactions")

    def load_images(self):
        with open("jsons/CRData.json", "r") as file:
            self.reactions = json.load(file)

    @commands.command()
    @is_admin()
    async def addemote(self, ctx, cmd, reaction):
        self.reactions[cmd] = reaction
        with open("jsons/CRData.json", "w") as file:
            json.dump(self.reactions, file, indent=4)
        await ctx.message.delete(delay=1)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith(settings["BOT_PREFIX"]):
            return
        emote = message.content[1:].split()[0]
        if emote in self.reactions.keys():
            embed = discord.Embed(color=discord.Colour.purple(), type="rich")
            embed.set_image(url=self.reactions[emote])
            await message.channel.send(embed=embed)


def setup(client):
    client.add_cog(CustomReactions(client))
