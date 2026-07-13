from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# Import the specific exceptions from the library
from youtube_transcript_api import (
    YouTubeTranscriptApi, 
    TranscriptsDisabled, 
    NoTranscriptFound, 
    VideoUnavailable
)
import re
import traceback
import asyncio
import yt_dlp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    """
    Extracts the 11-character YouTube video ID from any standard, 
    shortened, embedded, or Shorts URL format.
    Acceptable URL formats includes:
    - Standard: https://www.youtube.com/watch?v={Video_ID}
    - Shortened: https://youtu.be/{Video_ID}
    - Embedded: https://www.youtube.com/embed/{Video_ID}
    - Shorts: https://www.youtube.com/shorts/{Video_ID}
    - URL with params: https://www.youtube.com/watch?v={Video_ID}&t=90s
    - HTTP & alternate domains
    """
    # Strips surrounding whitespaces
    url = url.strip()
    
    # Modern lookahead pattern to capture exactly 11 characters after common YouTube URL structures
    pattern = (
        r'(?:https?://)?'          # Optional http or https
        r'(?:www\.)?'              # Optional www.
        r'(?:'                     # Non-capturing group for domain matches
        r'youtube\.com/'           # youtube.com
        r'(?:watch\?v=|shorts/|embed/|v/|e(?:mbed)?/|.*[?&]v=)' # Paths containing the ID
        r'|youtu\.be/'             # Or youtu.be short domain
        r')'
        r'([^"&?/\s]{11})'          # Captures exactly 11 alphanumeric/special characters making up the ID
    )
    
    match = re.search(pattern, url)
    return match.group(1) if match else None

def format_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}" if hrs > 0 else f"{mins:02d}:{secs:02d}"

# --- BLOCKING HELPER FUNCTIONS RUN CONCURRENTLY ---

def fetch_youtube_metadata(url: str):
    """
    Uses yt-dlp to extract the video title and description.
    """
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            "title": info.get("title", "Unknown Title"),
            "description": info.get("description", "No description available.")
        }

def fetch_youtube_transcript(video_id: str):
    """
    Uses youtube-transcript-api with fallback mechanics.
    """
    yt_api = YouTubeTranscriptApi()
    try:
        raw_transcript = yt_api.fetch(video_id)
    except NoTranscriptFound:
        transcript_list = yt_api.list(video_id)
        all_transcripts = list(transcript_list._manually_created_transcripts.values()) + \
                          list(transcript_list._generated_transcripts.values())
        
        if not all_transcripts:
            raise Exception("No transcripts available in any language for this video.")
            
        raw_transcript = all_transcripts[0].fetch()
        
    return [
        {"timestamp": format_time(entry.start), "text": entry.text}
        for entry in raw_transcript
    ]

# --- PARALLELIZED ENDPOINT ---

@app.post("/transcript")
async def get_transcript(request: VideoRequest):
    video_id = extract_video_id(request.url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format.")
    
    try:
        # Spin up both tasks concurrently in separate threads to avoid blocking FastAPI's event loop
        metadata_task = asyncio.to_thread(fetch_youtube_metadata, request.url)
        transcript_task = asyncio.to_thread(fetch_youtube_transcript, video_id)
        
        # Await both parallel tasks at the exact same time
        metadata, transcript_data = await asyncio.gather(metadata_task, transcript_task)
        
        return {
            "video_id": video_id,
            "title": metadata["title"],
            "description": metadata["description"],
            "transcript": transcript_data
        }
        
    except Exception as e:
        print("\n--- DETAILED BACKEND ERROR ---")
        traceback.print_exc()
        print("------------------------------\n")
        
        error_msg = str(e).lower()
        if "disabled" in error_msg:
            raise HTTPException(status_code=400, detail="Subtitles are disabled for this video.")
        elif "unavailable" in error_msg:
            raise HTTPException(status_code=404, detail="This video is unavailable or private.")
            
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to process video: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)