import yt_dlp
import re

def get_youtube_transcript(url):
    """
    Extract transcript from YouTube video using yt-dlp.
    Falls back to auto-generated captions if manual transcripts aren't available.
    
    Args:
        url (str): YouTube video URL
        
    Returns:
        str: Video transcript text
    """
    ydl_opts = {
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract info to get available subtitles
            info = ydl.extract_info(url, download=False)
            
            # Try to get manual subtitles first, then auto-generated
            subtitles = info.get('subtitles', {})
            automatic_captions = info.get('automatic_captions', {})
            
            # Look for English subtitles
            subtitle_url = None
            if 'en' in subtitles:
                # Prefer manual subtitles
                subtitle_url = subtitles['en'][0]['url']
            elif 'en' in automatic_captions:
                # Fall back to auto-generated captions
                subtitle_url = automatic_captions['en'][0]['url']
            
            if not subtitle_url:
                raise Exception("No English subtitles available for this video")
            
            # Download and parse the subtitle file
            import requests
            response = requests.get(subtitle_url)
            subtitle_content = response.text
            
            # Parse SRT format (simple parsing)
            transcript_parts = []
            srt_blocks = re.split(r'\n\s*\n', subtitle_content)
            
            for block in srt_blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Skip the number and timestamp lines, get the text
                    text_lines = lines[2:]
                    text = ' '.join(text_lines)
                    if text.strip():
                        transcript_parts.append(text.strip())
            
            transcript = ' '.join(transcript_parts)
            
            if not transcript.strip():
                raise Exception("Could not extract transcript text")
            
            return transcript
            
        except Exception as e:
            raise Exception(f"Failed to extract transcript from YouTube video: {str(e)}")

if __name__ == "__main__":
    # Test the function
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll for testing
    try:
        transcript = get_youtube_transcript(test_url)
        print(f"Transcript: {transcript[:200]}...")  # Print first 200 chars
    except Exception as e:
        print(f"Error: {e}")
