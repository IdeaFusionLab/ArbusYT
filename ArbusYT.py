import os

from dotenv import load_dotenv
from pytube import YouTube
import discord
from discord import app_commands, Intents, Interaction, Client

load_dotenv()
DISCORD_BOT_TOKEN_YT = os.getenv('DISCORD_BOT_TOKEN_YT')

DOMAINS = ['youtube','youtu.be']

ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True
}

class MusicBot(Client):

    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.channel = None
        self.queue = []

    async def join_voice_channel(self, interaction: Interaction):
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()
        self.channel = channel

    async def play_audio_source(self, interaction: Interaction, url: str):
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        voice = interaction.guild.voice_client
        voice.stop()
        audio_source = discord.FFmpegPCMAudio(video.url, **FFMPEG_OPTIONS)
        
        voice.play(audio_source,after=lambda e : self.loop.create_task(self.play_next()))


    def enqueue(self, url: str):
        self.queue.append(url)

    async def play_next(self):
        if len(self.queue) > 0:
            next_url = self.queue.pop(0)
            await self.play_audio_source(self.channel, next_url)

    async def skip(self, interaction: Interaction):

        if not bot.channel or not bot.channel.guild.voice_client or not bot.channel.guild.voice_client.is_playing() or len(bot.queue) == 0:
            await bot.leave_voice_channel(interaction)
            return
        bot.channel.guild.voice_client.stop()
        await interaction.response.send_message("Canción saltada.")
        
        await self.play_next()

    async def leave_voice_channel(self, interaction: Interaction):
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect()
            bot.channel = None
            bot.queue = []
            await interaction.response.send_message('He abandonado el canal de voz.')

    async def on_ready(self):
        print(f'{self.user} se ha conectado a Discord!')
        await self.tree.sync(guild=None)

bot = MusicBot(intents=Intents.default())

def check_yt_url(url):
    url_in_domain = False
    for domain in DOMAINS:
        if domain in url:
            url_in_domain = True
    return url_in_domain

#Commands

@bot.tree.command()
async def join(interaction: Interaction):
    await bot.join_voice_channel(interaction)
    await interaction.response.send_message('Me he unido al canal de voz.')

@bot.tree.command()
async def stop(interaction: Interaction):
    await bot.leave_voice_channel(interaction)

@bot.tree.command()
async def play(interaction: Interaction, url: str):
    if not check_yt_url(url):
        await interaction.response.send_message("Url no valida.")
        return
    if interaction.user.voice is None:
        await interaction.response.send_message("Debes estar en un canal de voz para usar este comando.")
    else:
        if not bot.channel:
            await bot.join_voice_channel(interaction)

        bot.enqueue(url)

        await interaction.response.send_message(f'Agregado a la cola: {url}')
        
        if not bot.channel.guild.voice_client.is_playing():
           await bot.play_next()
        
@bot.tree.command()
async def skip(interaction: Interaction):
    await bot.skip(interaction)

bot.run(DISCORD_BOT_TOKEN_YT)
