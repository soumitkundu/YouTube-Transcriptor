import re

def extract_video_id(url):
    # Regex pattern to catch all standard, short, shorts, embed, and live YouTube URLs
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

# Test cases for all formats
urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",
    "https://www.youtube.com/shorts/dQw4w9WgXcQ",
    "https://www.youtube.com/embed/dQw4w9WgXcQ",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=90s",
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL123",
    "http://youtube.com/watch?v=dQw4w9WgXcQ"
]

results = {url: extract_video_id(url) for url in urls}
print(results)
