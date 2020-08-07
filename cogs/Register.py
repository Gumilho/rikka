import json
import discord
from discord.ext import commands, tasks


def is_admin():
    async def predicate(ctx):
        return any(filter(lambda role: role.name == "Admin", ctx.author.roles))
    return commands.check(predicate)


class Register(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.public_projects = {}
        self.private_projects = {}
        with open("jsons/settings.json", "r") as f:
            self.settings = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update.start()
        print("Loaded Register")

    def save_json(self):

        with open("jsons/private_projects.json", "w") as f:
            json.dump(self.private_projects, f, indent=4)

        with open("jsons/public_projects.json", "w") as f:
            json.dump(self.public_projects, f, indent=4)

    def load_json(self):

        with open("jsons/public_projects.json", "r") as f:
            self.public_projects = json.load(f)

        with open("jsons/private_projects.json", "r") as f:
            self.private_projects = json.load(f)

    async def __create_channel(self, short_title, guild):
        print("Called create_category")
        role = await guild.create_role(name=short_title)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
            role: discord.PermissionOverwrite(read_messages=True),
        }
        category = self.bot.get_channel(self.settings["DOWNCATID"])
        await guild.create_text_channel(short_title, category=category, overwrites=overwrites)
        print("Channel created")

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
        channel_id = self.settings["PRIPRJID"]
        private_message = await self.bot.get_channel(channel_id).send(private_text)
        self.private_projects[private_message.id] = private_dict

    async def __public_send(self, title, short_title, sinopsis, image, genres):
        print("called __public_send")
        color = self.settings["EMBED_COLOR"]
        embed = discord.Embed(color=color, type="rich")
        embed.set_image(url=image)
        embed.add_field(name=title, value=sinopsis, inline=False)
        embed.add_field(name="Gêneros", value=genres, inline=False)

        public_project_channel = self.bot.get_channel(self.settings["PUBPRJID"])
        public_message = await public_project_channel.send(embed=embed)
        await public_message.add_reaction(self.settings["emoji"]["viewer"])
        self.public_projects[public_message.id] = [short_title, embed.to_dict()]
        self.save_json()

    async def __update_public(self):
        public_project_channel = self.bot.get_channels(self.settings["PUBPRJID"])
        async for message in public_project_channel.history():
            await self.__update_public_message(message)

    async def __update_public_message(self, message):
        for reaction in message.reactions:
            if str(reaction.emoji) == self.settings["emoji"]["viewer"]:
                role = discord.utils.get(message.guild.roles, name=self.public_projects[str(message.id)][0])
                # Remove all manga roles
                for member in message.guild.members:
                    if role in member.roles:
                        await member.remove_roles(role)
                # Add manga roles
                async for user in reaction.users():
                    if user.name != "Rikka":
                        await user.add_roles(role)

    async def __update_private(self):
        private_project_channel = self.bot.get_channels(self.settings["PRIPRJID"])
        async for message in private_project_channel.history():
            await self.__update_private_message(message)

    def __change_json(self, args):
        for key, project in self.private_projects.items():
            if project["name"].lower() == args[0].lower():
                project["roles"][args[1].title()].append(args[2])
                self.private_projects[key] = project
                self.save_json()
                return key

    async def __update_private_message(self, message):
        project = self.private_projects[str(message.id)]
        new_content = f"```{project['name']} \n" \
                      f"\n\tCleaning: {' '.join(project['roles']['Cleaning'])}" \
                      f"\n\tRedraw: {' '.join(project['roles']['Redraw'])}" \
                      f"\n\tTraducao: {' '.join(project['roles']['Traducao'])}" \
                      f"\n\tTypesetting: {' '.join(project['roles']['Typesetting'])}```"
        await message.edit(content=new_content)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.member == self.bot.user:
            return
        if payload.channel_id == self.settings["PUBPRJID"]:
            if str(payload.emoji) == self.settings["emoji"]["viewer"]:
                guild = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, name=self.public_projects[str(payload.message_id)][0])
                member = guild.get_member(payload.user_id)
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.member == self.bot.user:
            return
        if payload.channel_id == self.settings["PUBPRJID"]:
            if str(payload.emoji) == self.settings["emoji"]["viewer"]:
                guild = self.bot.get_guild(payload.guild_id)
                role = discord.utils.get(guild.roles, name=self.public_projects[str(payload.message_id)][0])
                member = guild.get_member(payload.user_id)
                await member.remove_roles(role)

    @commands.command()
    @commands.has_role("Admin")
    async def addmember(self, ctx, *args):
        key = self.__change_json(args)
        private_project_channel = self.bot.get_channel(self.settings["PRIPRJID"])
        message = await private_project_channel.fetch_message(int(key))
        await self.__update_private_message(message)
        await ctx.message.delete(delay=2)

    @commands.command()
    @commands.has_role("Admin")
    async def addproject(self, ctx, *args):
        guild = ctx.guild
        title, short_title, sinopsis, image, genres = args
        await self.__create_channel(short_title, guild)
        await self.__private_send(short_title)
        await self.__public_send(title, short_title, sinopsis, image, genres)
        await ctx.message.delete(delay=2)

    @commands.command()
    @commands.has_role("Admin")
    @tasks.loop(hours=1)
    async def update(self):
        self.load_json()
        await self.__update_public()
        await self.__update_private()

    @addproject.error
    async def addproject_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            pass


def setup(client):
    client.add_cog(Register(client))
