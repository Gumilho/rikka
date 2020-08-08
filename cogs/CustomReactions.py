import json
import discord
from discord.ext import commands


class CustomReactions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reactions = {}
        with open("jsons/settings.json", "r") as f:
            self.settings = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        self.load_images()
        print("Loaded CustomReactions")

    def load_images(self):
        with open("jsons/CRData.json", "r") as f:
            self.reactions = json.load(f)

    @commands.command()
    @commands.has_role("Admin")
    async def addemote(self, ctx, cmd, reaction):
        self.reactions[cmd] = reaction
        with open("jsons/CRData.json", "w") as file:
            json.dump(self.reactions, file, indent=4)
        await ctx.message.delete(delay=1)

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.content.startswith(self.settings["BOT_PREFIX"]):
            return
        emote = message.content[1:].split()[0]
        if emote in self.reactions.keys():
            embed = discord.Embed(color=discord.Colour.purple(), type="rich")
            embed.set_image(url=self.reactions[emote])
            await message.channel.send(embed=embed)


def setup(client):
    client.add_cog(CustomReactions(client))
