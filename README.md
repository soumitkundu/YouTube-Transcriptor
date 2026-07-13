# YouTube-Transcriptor
Paste a YouTube video URL and download transcript of the given video

## Strp-by-Step development guide

### First create and activate a virtual Environment:

**Run this command to create a Dev Environment:**

```
py -m venv .venv
```

**Activate the environment**

```
.venv/Scripts/activate
```

### Install Dependencies

```
pip install fastapi uvicorn youtube-transcript-api
```

### Create `main.py`

This script sets up a single POST endpoint (`/transcript`). It extracts the unique 11-character video ID from standard YouTube links or short links (e.g., `youtu.be`) and fetches the transcript data.

### Run the Backend

**To run your backend**: Just execute `py main.py`. It will start a local server at `http://127.0.0.1:8000`. You can even visit `http://127.0.0.1:8000/docs` to see the auto-generated Swagger UI documentation!

Try the backend API using the a youtube url for testing (e.g. `https://www.youtube.com/watch?v=jNQXAC9IVRw`)

Now come to **Front-end**

### Create React App

```
npx create-react-app youtube-transcriptor-frontend
```

Then open the directory in the terminal

```
cd youtube-transcriptor-frontend
```

Replace `src/App.js` and `src/App.css` given here

### Run the Front-end service

To run your frontend: Run (_inside the react directory_).

```
npm start
```

_It will open `http://localhost:3000`_

You can try the same youtube URL to test `https://www.youtube.com/watch?v=jNQXAC9IVRw`

---

### Handling Non-English transcripts

By default `youtube-transcript-api` looking for strictly an English ('en') transcript if no language is specified.

To make the application robust and capable of handling non-English, manual or auto-generated video transcripts without crashing, I have added a **Language Fallback Strategy**.

### 🛠️ The Strategy

1. We will try to fetch the default language (English).
2. If it fails with `NoTranscriptFound`, we will fetch the transcript list for that video, look for *any* language that is auto-generated or manually created, and grab the first one available one.

### Allowed YouTube Video URLs

To handle with different kind of YouTube URLs I have made `extract_video_id()` function applicable for any standard, shortened, embedded, or Shorts URL format.

**Acceptable URL formats includes:**

- Standard: https://www.youtube.com/watch?v={Video_ID}
- Shortened: https://youtu.be/{Video_ID}
- Embedded: https://www.youtube.com/embed/{Video_ID}
- Shorts: https://www.youtube.com/shorts/{Video_ID}
- URL with params: https://www.youtube.com/watch?v={Video_ID}&t=90s
- HTTP & alternate domains

---

### Extract Video Metadata:

> Extracted Title and Description of the given video

**Install `yt-dlp`**

```Bash
pip install yt-dlp
```

Used `yt-dlp`, because it is a free choice for grabbing metadata like titles and descriptions without dealing with official YouTube API quotas or keys.

To run both tasks in parallel—fetching the transcript and extracting video metadata—I have utilized Python's built-in `asyncio.to_thread`. Since both operations are network-bound (I/O) blocking calls, running them concurrently will drastically speed up your API's response time.

### Added `requirements.txt`

As we are moving forword its required to maintain all the dependencies in a single source. So I have added `requirements.txt` file to smoothly install all the requirements using a single command

**To install the dependencies simple run this command:**

```bash
pip install -r requirements.txt
```
