import json
import discord
from discord.ext import commands

with open("jsons/settings.json", "r") as f:
    settings = json.load(f)


def is_admin():
    async def predicate(ctx):
        return any(filter(lambda role: role.name == "Admin", ctx.author.roles))

    return commands.check(predicate)


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.public_projects = {}
        self.private_projects = {}
        self.username_dict = {
            "𝓟 🅞🅔🅜^🅤^": "Poemu",
            "Manu": "Manu",
            "Daby": "Daby",
            "Gumi": "Gumi",
            "Rin": "Rin",
            "Carlos Marcos": "Carlos Marcos",
            "Nana": "Nana"
        }

    @commands.Cog.listener()
    async def on_ready(self):
        with open("jsons/public_projects.json", "r") as f:
            self.public_projects = json.load(f)

        with open("jsons/private_projects.json", "r") as f:
            self.private_projects = json.load(f)

        await self.__update_public()
        await self.__update_private()
        # await self.__update_message_public()
        print("Loaded Register")

    async def __create_channels(self, short_title, guild):
        print("called create_category")
        role = await guild.create_role(name=short_title)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        category = self.bot.get_channel(settings["DOWNCATID"])
        await guild.create_text_channel(short_title, category=category, overwrites=overwrites)

    async def __private_send(self, short_title):
        print("called __private_send")
        private_text = f"```{short_title}\n" \
                       f"\n\tCleaning: " \
                       f"\n\tRedraw: " \
                       f"\n\tTraducao: " \
                       f"\n\tTypesetting: ``` "
        private_dict = {
            "name": short_title,
            "roles": {
                "Cleaning": [],
                "Redraw": [],
                "Traducao": [],
                "Typesetting": [],
            }
        }
        channel_id = settings["PRIPRJID"]
        private_message = await self.bot.get_channel(channel_id).send(private_text)
        self.private_projects[private_message.id] = private_dict
        await private_message.add_reaction(settings["emoji"]["cleaner"])
        await private_message.add_reaction(settings["emoji"]["redrawer"])
        await private_message.add_reaction(settings["emoji"]["translator"])
        await private_message.add_reaction(settings["emoji"]["typesetter"])
        with open("jsons/private_projects.json", "w") as f:
            json.dump(self.private_projects, f, indent=4)
        # await self.__update_private()

    async def __public_send(self, title, short_title, sinopsis, image, genres):
        print("called __public_send")
        color = settings["EMBED_COLOR"]
        embed = discord.Embed(color=color, type="rich")
        embed.set_image(url=image)
        embed.add_field(name=title, value=sinopsis, inline=False)
        embed.add_field(name="Gêneros", value=genres, inline=False)

        channel_id = settings["PUBPRJID"]
        public_message = await self.bot.get_channel(channel_id).send(embed=embed)
        await public_message.add_reaction(settings["emoji"]["viewer"])
        self.public_projects[public_message.id] = [short_title, embed.to_dict()]
        with open("jsons/public_projects.json", "w") as f:
            json.dump(self.public_projects, f, indent=4)
        # await self.__update_public()

    async def __update_public(self):
        async for message in self.bot.get_channel(settings["PUBPRJID"]).history():
            for reaction in message.reactions:
                if reaction.emoji == settings["emoji"]["viewer"]:
                    role = discord.utils.get(message.guild.roles, name=self.public_projects[str(message.id)][0])

                    # Remove all manga roles
                    for member in message.guild.members:
                        if role in member.roles:
                            await member.remove_roles(role)

                    # Add manga roles
                    async for user in reaction.users:
                        if user.name != "Rikka":
                            await user.add_roles(role)

    async def __update_private(self):
        async for message in self.bot.get_channel(settings["PRIPRJID"]).history():
            for reaction in message.reactions:
                react_dict = {
                    settings["emoji"]["translator"]: "Traducao",
                    settings["emoji"]["cleaner"]: "Cleaning",
                    settings["emoji"]["redrawer"]: "Redraw",
                    settings["emoji"]["typesetter"]: "Typesetting"
                }
                role = react_dict[str(reaction.emoji)]
                team = [user.nick async for user in reaction.users() if user.name != "Rikka"]
                self.private_projects[str(message.id)]["roles"][role] = team
                with open("jsons/private_projects.json", "w") as f:
                    json.dump(self.private_projects, f, indent=4)
            await self.__update_message(message)

    async def __update_message_public(self):
        async for message in self.bot.get_channel(settings["PUBPRJID"]).history():
            if message.id == 734618114624585809:
                embed = message.embeds[0]
                embed.set_image(url="https://cdn.novelupdates.com/images/2019/11/F6F8ABE9-5B00-4941-80A1-996592C6976D.jpeg")
                await message.edit(embed=embed)

    async def __update_message(self, message):
        short_title = self.private_projects[str(message.id)]["name"]
        new_content = f"```{short_title} \n" \
                      f"\n\tCleaning: {' '.join(self.private_projects[str(message.id)]['roles']['Cleaning'])}" \
                      f"\n\tRedraw: {' '.join(self.private_projects[str(message.id)]['roles']['Redraw'])}" \
                      f"\n\tTraducao: {' '.join(self.private_projects[str(message.id)]['roles']['Traducao'])}" \
                      f"\n\tTypesetting: {' '.join(self.private_projects[str(message.id)]['roles']['Typesetting'])}```"
        await message.edit(content=new_content)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member == self.bot.user:
            return
        if str(payload.message_id) in self.public_projects.keys():
            await self.__update_public()
        elif str(payload.message_id) in self.private_projects.keys():
            await self.__update_private()

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.member == self.bot.user:
            return
        if str(payload.message_id) in self.public_projects.keys():
            await self.__update_public()
        elif str(payload.message_id) in self.private_projects.keys():
            await self.__update_private()

    @commands.command()
    @is_admin()
    async def ap(self, ctx, *args):
        guild = ctx.guild
        try:
            title, short_title, sinopsis, image, genres = args
        except ValueError:
            print('numero errado de argumentos')
            return
        await self.__create_channels(short_title, guild)
        await self.__private_send(short_title)
        await self.__public_send(title, short_title, sinopsis, image, genres)
        await ctx.message.delete(delay=2)

    @ap.error
    async def ap_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass


def setup(client):
    client.add_cog(Register(client))
