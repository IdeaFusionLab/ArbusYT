import os
import youtube_dl
import discord
from discord import app_commands, Intents, Interaction, Client
from dotenv import load_dotenv

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

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

    async def join_voice_channel(self, interaction: Interaction):
        channel = interaction.user.voice.channel
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.move_to(channel)
        else:
            await channel.connect()

    async def play_audio_source(self, interaction: Interaction, url: str):
        ytdl = youtube_dl.YoutubeDL(ytdl_opts)
        info = ytdl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
        }
        voice = interaction.guild.voice_client
        voice.stop()
        audio_source = discord.FFmpegPCMAudio(url2, **FFMPEG_OPTIONS)
        voice.play(audio_source)

    async def on_ready(self):
        print(f'{self.user} se ha conectado a Discord!')
        await self.tree.sync(guild=None)

bot = MusicBot(intents=Intents.default())

@bot.tree.command()
async def join(interaction: Interaction):
    await bot.join_voice_channel(interaction)
    await interaction.response.send_message('Me he unido al canal de voz.')

@bot.tree.command()
async def leave(interaction: Interaction):
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message('He abandonado el canal de voz.')

@bot.tree.command()
async def play(interaction: Interaction, url: str):
    if interaction.user.voice is None:
        await interaction.response.send_message("Debes estar en un canal de voz para usar este comando.")
    else:
        await bot.join_voice_channel(interaction)
        await bot.play_audio_source(interaction, url)
        await interaction.response.send_message(f'Reproduciendo: {url}')

bot.run(DISCORD_BOT_TOKEN)
