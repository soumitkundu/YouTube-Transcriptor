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
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/\s]{11})'
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
        # Initialize the modern instance
        yt_api = YouTubeTranscriptApi()
        
        # Fetch the transcript data directly using the updated instance method
        raw_transcript = yt_api.fetch(video_id)
        
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
        
        # Return clean feedback if the error is due to video constraints
        error_msg = str(e).lower()
        if "disabled" in error_msg:
            raise HTTPException(status_code=400, detail="Subtitles are disabled for this video.")
        elif "unavailable" in error_msg:
            raise HTTPException(status_code=404, detail="This video is unavailable or private.")
            
        raise HTTPException(
            status_code=500, 
            detail="Failed to retrieve transcript. Check if the video supports captions."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)