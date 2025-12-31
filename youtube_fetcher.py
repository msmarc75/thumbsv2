import yt_dlp

def fetch_channel_videos(channel_url):
    """
    Fetches all videos from a YouTube channel.
    Returns a list of dictionaries with 'title' and 'url'.
    """
    ydl_opts = {
        'extract_flat': True,  # Don't download videos, just extract metadata
        'ignoreerrors': True,
        'quiet': True,
    }

    videos = []
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(channel_url, download=False)
            
            if 'entries' in info:
                # It's a playlist or channel
                for entry in info['entries']:
                    if entry:
                        title = entry.get('title')
                        url = entry.get('url')
                        # yt-dlp might return just the ID in url for flat extraction
                        if url and not url.startswith('http'):
                            url = f"https://www.youtube.com/watch?v={url}"
                            
                        if title and url:
                            videos.append({'title': title, 'url': url})
            else:
                # It's a single video?
                title = info.get('title')
                url = info.get('webpage_url') or info.get('url')
                if title and url:
                    videos.append({'title': title, 'url': url})
                    
    except Exception as e:
        print(f"Error fetching channel: {e}")
        return []

    return videos
