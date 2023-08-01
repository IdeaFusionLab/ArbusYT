import os
from dotenv import load_dotenv
load_dotenv()

DISCORD_BOT_TOKEN_YT = os.getenv('DISCORD_BOT_TOKEN_YT')

DOMAINS = ['youtube', 'youtu.be']

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}