from youtube_transcript_api import YouTubeTranscriptApi

try:
    print("Testing the modern instance-based routine...")
    
    # 1. Instantiate the class first
    yt_api = YouTubeTranscriptApi()
    
    # 2. Call fetch on the instance with a known valid video ID
    data = yt_api.fetch("jNQXAC9IVRw")
    
    print("\n🎉 Success! First line parsed:")
    print(data[0])
except Exception as e:
    print("Error during test:", e)