import discord
import yt_dlp as ytdlp
import asyncio
import concurrent.futures
import os

SONG_DOWNLOAD_DIRECTORY = "downloads"
os.makedirs(SONG_DOWNLOAD_DIRECTORY, exist_ok=True)



# ytdlp options
ytdlp_format_options = {
    'format': 'bestaudio[ext=m4a]/bestaudio/bestaudio',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',  # search if no URL
    'outtmpl': os.path.join(SONG_DOWNLOAD_DIRECTORY, '%(id)s.%(ext)s'),  # save to downloads folder
}

# ffmpeg options
#needed to setup a static build of ffmpeg:
#cd ~
#wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-armhf-static.tar.xz
#tar xf ffmpeg-release-armhf-static.tar.xz
#cd ffmpeg-*-static
#sudo cp ffmpeg /usr/local/bin/
#sudo cp ffprobe /usr/local/bin/


ffmpeg_options = {
    'before_options': '',
    'options': '-vn'
}

#ytdlp extractor setup
ytdlp_extractor = ytdlp.YoutubeDL(ytdlp_format_options)
print("extractor called")
download_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)  # limit threads for download
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
        #print(f"extracted: {self.title}")

    @classmethod
    async def from_url(cls, url, *, stream=True):

        print("download?: ",not stream)
        #downlaod in a sep thread
        data = await asyncio.get_running_loop().run_in_executor(download_executor, lambda: ytdlp_extractor.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0] 

        #stream vs download
        if stream:
            filename = data['url']
        else:
            filename = ytdlp_extractor.prepare_filename(data)


        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
