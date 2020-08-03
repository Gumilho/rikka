import json
import discord
from discord.ext import commands

with open("jsons/settings.json", "r") as f:
    settings = json.load(f)


def is_admin():
    async def predicate(ctx):
        return any(filter(lambda role: role.name == "Admin", ctx.author.roles))

    return commands.check(predicate)


class WelcomeMessage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reactions = {}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded WelcomeMessage")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        color = settings["EMBED_COLOR_WELCOME"]
        embed = discord.Embed(color=color, type="rich", description="Olá\nLeia as #❗-regras antes de tudo")
        embed.set_image(url="https://imgur.com/a/PBLIxH2")
        embed.add_field(name="Recrutamento", value="Se você está aqui para recrutamento, deixe seu nome e o cargo que "
                                                   "quer fazer no canal #📣-recrutamento.\nUm staff (vulgo eu ou rin) "
                                                   "vai entrar em contato assim que puder", inline=False)
        await member.guild.system_channel.send(embed=embed)


def setup(client):
    client.add_cog(WelcomeMessage(client))
