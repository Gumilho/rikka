import json
import discord
from discord.ext import commands

def is_admin():
    async def predicate(ctx):
        return any(filter(lambda role: role.name == "Admin", ctx.author.roles))
    return commands.check(predicate)


class WelcomeMessage(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.reactions = {}
        with open("jsons/settings.json", "r") as f:
            self.settings = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded WelcomeMessage")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        color = self.settings["EMBED_COLOR_WELCOME"]
        user = member.mention
        regras = member.guild.get_channel(self.settings["REGRAS_ID"]).mention
        recrutamento = member.guild.get_channel(self.settings["RECRUIT_ID"]).mention
        embed = discord.Embed(color=color, type="rich", description=f"Olá, {user}!\nLeia as {regras} antes de tudo")
        embed.set_image(url=settings['WELCOME_IMAGE'])
        embed.add_field(name="Recrutamento", value=f"Se você está aqui para recrutamento, deixe seu nome e o cargo que "
                                                   f"quer fazer no canal {recrutamento}.\nUm staff (vulgo eu ou rin) "
                                                   f"vai entrar em contato assim que puder", inline=False)
        await member.guild.system_channel.send(embed=embed)


def setup(client):
    client.add_cog(WelcomeMessage(client))
