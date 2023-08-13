from pytube import YouTube
import discord
from discord.ext import commands
from discord import (
    app_commands,
    Intents,
    Interaction,
    Client,
    Button,
)
import asyncio

from utils import take_playlist_by_url, check_play_condition
from config import DISCORD_BOT_TOKEN_YT, FFMPEG_OPTIONS


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

    async def play_audio_source(
        self, channel, interaction: Interaction, url: str
    ):
        yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
        video = yt.streams.filter(only_audio=True).first()

        voice = channel.guild.voice_client
        voice.stop()
        audio_source = discord.FFmpegPCMAudio(video.url, **FFMPEG_OPTIONS)

        voice.play(
            audio_source,
            after=lambda e: self.loop.create_task(self.play_next(interaction)),
        )

        await interaction.followup.send(
            f"Reproduciendo esta cancion: {url}", view=SkipButton()
        )

    def enqueue(self, url: str):
        self.queue.append(url)
    #tst
    async def play_next(self, interaction):
        if not bot.channel.guild.voice_client.is_playing():
            if len(self.queue) > 0:
                next_url = self.queue.pop(0)
                await self.play_audio_source(
                    self.channel, interaction, next_url
                )

    async def skip(self, interaction: Interaction):
        if (
            not bot.channel
            or not bot.channel.guild.voice_client
            or not bot.channel.guild.voice_client.is_playing()
            or len(bot.queue) == 0
        ):
            await bot.leave_voice_channel(interaction)
            return
        bot.channel.guild.voice_client.stop()
        await interaction.response.send_message("Canción saltada.")

        await self.play_next(interaction)

    async def leave_voice_channel(self, interaction: Interaction, afk=False):
        if interaction.guild.voice_client is not None:
            await interaction.guild.voice_client.disconnect()
            bot.channel = None
            bot.queue = []
            if not afk:
                await interaction.response.send_message(
                    'He abandonado el canal de voz.'
                )

    async def check_and_disconnect(self, interaction: Interaction):
        while True:
            await asyncio.sleep(3 * 60)  # Espera 3 minutos

            if (
                self.channel is not None
                and not self.channel.guild.voice_client.is_playing()
                and len(self.queue) == 0
            ):
                await self.leave_voice_channel(interaction, True)
                break

    async def on_ready(self):
        print(f'{self.user} se ha conectado a Discord!')
        await self.tree.sync(guild=None)


bot = MusicBot(intents=Intents.default())


# Commands


@bot.tree.command()
async def join(interaction: Interaction):
    await bot.join_voice_channel(interaction)
    await interaction.response.send_message('Me he unido al canal de voz.')


@bot.tree.command()
async def stop(interaction: Interaction):
    await bot.leave_voice_channel(interaction)


@bot.tree.command()
async def play(interaction: Interaction, url: str):
    check_data = check_play_condition(interaction, url)
    if not check_data['is_valid']:
        await interaction.response.send_message(check_data['message'])
        return

    if not bot.channel:
        await bot.join_voice_channel(interaction)

    bot.enqueue(url)

    await interaction.response.send_message(f'Agregado a la cola: {url}')

    # Check if url is a playlist
    if "&list" in url:
        video_urls = take_playlist_by_url(url)

        for video_url in video_urls:
            bot.enqueue(video_url)

    # Reproduce video if none video is playing
    if not bot.channel.guild.voice_client.is_playing():
        await bot.play_next(interaction)
        bot.loop.create_task(bot.check_and_disconnect(interaction))


@bot.tree.command()
async def skip(interaction: Interaction):
    await bot.skip(interaction)


class SkipButton(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(
        label="Skip",
        style=discord.ButtonStyle.success,
        custom_id="skip_button",
    )
    async def skip_button_callback(
        self, interaction: Interaction, button: Button
    ):
        await interaction.response.send_message(content="Skipped video")
        await bot.skip(interaction)


bot.run(DISCORD_BOT_TOKEN_YT)
