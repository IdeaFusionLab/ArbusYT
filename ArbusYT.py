import os
import discord
from discord import app_commands, Intents
import youtube_dl
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv("EnvironmentVariables")

# Obtener el token del bot de Discord desde las variables de entorno
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Crea una instancia del bot
intents = Intents.default()
bot = app_commands.BotApp(intents=intents)

# Carga las opciones de youtube_dl
ytdl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'quiet': True
}

async def join_voice_channel(interaction):
    channel = interaction.user.voice.channel
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.move_to(channel)
    else:
        await channel.connect()

async def play_audio_source(interaction, url):
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

@bot.event
async def on_ready():
    print(f'{bot.user} se ha conectado a Discord!')

@bot.command()
async def join(interaction: discord.Interaction):
    await join_voice_channel(interaction)
    await interaction.response.send_message('Me he unido al canal de voz.')

@bot.command()
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client is not None:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message('He abandonado el canal de voz.')

@bot.command()
async def play(interaction: discord.Interaction, url: str):
    if interaction.user.voice is None:
        await interaction.response.send_message("Debes estar en un canal de voz para usar este comando.")
    else:
        await join_voice_channel(interaction)
        await play_audio_source(interaction, url)
        await interaction.response.send_message(f'Reproduciendo: {url}')

# Utiliza la variable DISCORD_BOT_TOKEN para iniciar el bot
bot.run(DISCORD_BOT_TOKEN)
