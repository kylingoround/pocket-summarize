import yt_dlp
import re

def get_video_metadata(url):
    """
    Extract metadata from YouTube video.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        dict: Video metadata including title, description, duration, etc.
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        "skip_download": True,
        "extract_flat": True,  
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            
            # Extract video ID from URL
            video_id = None
            if 'youtube.com/watch' in url:
                video_id = re.search(r'v=([^&]+)', url).group(1)
            elif 'youtu.be/' in url:
                video_id = url.split('youtu.be/')[-1].split('?')[0]
            
            metadata = {
                'title': info.get('title', 'Unknown Title'),
                'description': info.get('description', 'No description available'),
                'duration': info.get('duration', 0),  # in seconds
                'uploader': info.get('uploader', 'Unknown'),
                'upload_date': info.get('upload_date', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'video_id': video_id,
                'url': url
            }
            
            return metadata
        except Exception as e:
            raise Exception(f"Failed to extract video metadata: {str(e)}")

if __name__ == "__main__":
    # Test the function
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    try:
        metadata = get_video_metadata(test_url)
        print(f"Title: {metadata['title']}")
        print(f"Duration: {metadata['duration']} seconds")
        print(f"Uploader: {metadata['uploader']}")
    except Exception as e:
        print(f"Error: {e}")
