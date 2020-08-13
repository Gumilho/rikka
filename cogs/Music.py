import json
import re
import discord
from discord.ext import commands, tasks
import youtube_dl
from lxml.html import fromstring
from youtube_search import YoutubeSearch
import requests
import os


def download(arg):
    if re.compile(r'https?://(?:www\.)?.+').match(arg):
        r = requests.get(arg)
        title = fromstring(r.content).findtext('.//title')
        url = arg
    else:
        result = YoutubeSearch(arg, max_results=1).to_dict()[0]
        title = result['title']
        url = 'https://www.youtube.com' + result["url_suffix"]
    ydl_opts = {
        'outtmpl': f'songs/{title}.%(ext)s',
        'format': 'bestaudio/best',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return title


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.vc = None
        self.loop = False
        self.queue = []
        self.current = ''
        with open("jsons/settings.json", "r") as f:
            self.settings = json.load(f)

    @commands.Cog.listener()
    async def on_ready(self):
        self.update.start()
        print("Loaded Music")

    def play_next(self, e, filename):
        os.remove(filename)
        if self.queue:
            filename = self.queue.pop(0)
            self.vc.play(discord.FFmpegOpusAudio(filename), after=lambda e: self.play_next(e, filename))
            if self.loop:
                self.queue.append(filename)

    @tasks.loop(minutes=1)
    async def update(self):
        if not isinstance(self.vc, discord.VoiceClient):
            return
        print(self.queue)
        print(self.vc.is_playing())
        if not self.queue and not self.vc.is_playing():
            await self.vc.disconnect()

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, arg):
        print('Command play')
        channel = ctx.author.voice.channel
        print(self.vc)
        if self.vc is None:
            self.vc = await channel.connect()
        if not self.vc.is_connected():
            self.vc = await channel.connect()
        title = download(arg)
        if not self.vc.is_playing():
            filename = 'songs/' + title + '.webm'
            self.current = filename
            self.vc.play(discord.FFmpegPCMAudio(filename), after=lambda e: self.play_next(e, filename))
        else:
            self.queue.append('songs/' + title + '.webm')

    @commands.command(aliases=['s'])
    async def stop(self, ctx):
        print('Command stop')
        if self.vc.is_playing():
            self.vc.stop()

    @commands.command()
    async def pause(self, ctx):
        print('Command pause')
        if self.vc.is_playing():
            self.vc.pause()

    @commands.command()
    async def resume(self, ctx):
        print('Command resume')
        if self.vc.is_paused():
            self.vc.resume()

    @commands.command()
    async def skip(self, ctx):
        print('Command skip')
        if self.vc.is_playing():
            self.vc.stop()
            self.play_next(None, self.current)


def setup(client):
    client.add_cog(Music(client))
