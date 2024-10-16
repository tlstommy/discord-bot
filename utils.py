import discord
import yt_dlp as ytdlp
import asyncio

#ytdlp options
ytdlp_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',#search if no url
}

#ffmpeg ops
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',  #disable video
}

ytdlp_extractor = ytdlp.YoutubeDL(ytdlp_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdlp_extractor.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]#grab top item

        filename = data['url'] if stream else ytdlp_extractor.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)