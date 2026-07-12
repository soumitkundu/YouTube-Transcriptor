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

from youtube_transcript_api._errors import NoTranscriptFound

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
    - Standard: https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - Shortened: https://youtu.be/dQw4w9WgXcQ
    - Embedded: https://www.youtube.com/embed/dQw4w9WgXcQ
    - Shorts: https://www.youtube.com/shorts/dQw4w9WgXcQ
    - URL with params: https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=90s
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

@app.post("/transcript")
async def get_transcript(request: VideoRequest):
    video_id = extract_video_id(request.url)
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid YouTube URL format.")
    
    try:
        yt_api = YouTubeTranscriptApi()
        
        try:
            # 1. First attempt: Try fetching standard English transcript
            raw_transcript = yt_api.fetch(video_id)
        except NoTranscriptFound:
            print(f"English transcript not found for {video_id}. Attempting language fallback...")
            
            # 2. Fallback: Retrieve the list of all available transcripts for this video
            transcript_list = yt_api.list(video_id)
            
            # 3. Find the first available transcript regardless of the language code
            # This loops through manually created or generated transcripts
            all_transcripts = list(transcript_list._manually_created_transcripts.values()) + \
                              list(transcript_list._generated_transcripts.values())
            
            if not all_transcripts:
                raise Exception("No transcripts available in any language for this video.")
                
            # Pick the first transcript object available (e.g., Hindi auto-generated)
            fallback_transcript_obj = all_transcripts[0]
            raw_transcript = fallback_transcript_obj.fetch()
        
        # Format the output using dot notation
        formatted_transcript = [
            {"timestamp": format_time(entry.start), "text": entry.text}
            for entry in raw_transcript
        ]
        return {"video_id": video_id, "transcript": formatted_transcript}
        
    except Exception as e:
        import traceback
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
            detail=f"Failed to retrieve transcript: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)