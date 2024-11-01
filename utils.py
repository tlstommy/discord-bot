import discord
import yt_dlp as ytdlp
import asyncio
import concurrent.futures

# ytdlp options
ytdlp_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',  # search if no URL
}

# ffmpeg options
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -bufsize 512k',
}

#ytdlp extractor setup
ytdlp_extractor = ytdlp.YoutubeDL(ytdlp_format_options)
print("extractor called")
download_executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)  # limit threads for download
print("executor called")
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        
        # Extracted data for display
        self.title = data.get('title')
        self.link_url = data.get('webpage_url')
        self.length = data.get('duration_string')
        self.thumbnail = data.get('thumbnail')
        self.uploader = data.get('uploader')
        print(f"extracted: {self.title}")

    @classmethod
    async def from_url(cls, url, *, stream=True):
        #downlaod in a sep thread
        data = await asyncio.get_running_loop().run_in_executor(download_executor, lambda: ytdlp_extractor.extract_info(url, download=False))

        if 'entries' in data:
            data = data['entries'][0] 

        #grab data
        filename = data['url']
        print("got filename")
        print(filename)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
