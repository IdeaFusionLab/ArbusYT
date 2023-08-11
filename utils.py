from pytube import  Playlist
from discord import (
    Interaction
)

from config import  DOMAINS

def take_playlist_by_url(url:str):
    playlist = Playlist(url)
    index = 0
    if 'index=' in url:
        for section in url.split('&'):
            if 'index=' in section:
                index = int(section.split('index=')[1])

    video_urls = list(playlist.video_urls)
    return video_urls[index - 1 :]

def check_play_condition(interaction:Interaction,url:str):
    data_check = {}
    if not check_yt_url(url):
        data_check['message'] = 'Url no valida'
        data_check['is_valid'] = False
        return data_check
    if interaction.user.voice is None:
        data_check['message'] = 'Debes estar en un canal de voz para usar este comando.'
        data_check['is_valid'] = False
        return data_check
    
    data_check['is_valid'] = True
    return data_check

def check_yt_url(url:str):
    url_in_domain = False
    for domain in DOMAINS:
        if domain in url:
            url_in_domain = True
    return url_in_domain