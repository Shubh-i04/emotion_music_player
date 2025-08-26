# music_youtube.py
import webbrowser
import yt_dlp

def get_youtube_url(query: str) -> str | None:
    """Use yt-dlp search to get the first YouTube result URL for the query."""
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
        "default_search": "ytsearch1",  # search and pick the first result
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            video = info["entries"][0] if "entries" in info else info
            return video.get("webpage_url")
    except Exception as e:
        print("YouTube search error:", e)
        return None

def open_on_youtube(query: str):
    """Open the first matching YouTube result in the browser."""
    url = get_youtube_url(query)
    if url:
        webbrowser.open(url)
        return True
    return False
