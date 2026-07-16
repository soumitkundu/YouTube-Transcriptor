import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [transcript, setTranscript] = useState([]);
  const [videoInfo, setVideoInfo] = useState({ title: '', description: '', id: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const apiURL = 'http://127.0.0.1:8000';
  // const apiURL = 'https://5e81-223-223-144-104.ngrok-free.app';  // Local Ngrok URL for testing

  const fetchTranscript = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError('');
    setTranscript([]);
    setVideoInfo({ title: '', description: '', id: '' });

    try {
      const response = await fetch(apiURL + '/transcript', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }

      setTranscript(data.transcript);
      setVideoInfo({ title: data.title, description: data.description, id: data.video_id });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // --- UTILITY FUNCTIONS FOR COPY & DOWNLOAD ---

  // Helper to remove emojis, symbols, and replace spaces/slashes with underscores
  const getCleanFileName = (title, id, suffix, extension) => {
    const cleanTitle = title
      .replace(/[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDC00-\uDFFF]/g, '') // Remove emojis
      .replace(/[^\w\s-]/g, '') // Remove special characters except alphanumeric, spaces, and hyphens
      .trim()
      .replace(/\s+/g, '_'); // Replace spaces with underscore

    return suffix ? `${cleanTitle}-${id}-${suffix}.${extension}` : `${cleanTitle}-${id}.${extension}`;
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard! 📋');
  };

  const downloadFile = (content, fileName, contentType) => {
    const a = document.createElement('a');
    const file = new Blob([content], { type: contentType });
    a.href = URL.createObjectURL(file);
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  // Build the full plain text transcript (Timestamp + Text)
  const getPlainTextTranscript = () => {
    return transcript.map(item => `[${item.timestamp}] ${item.text}`).join('\n');
  };

  // Helper function to build the text-only (without timestamps) version of the transcript for `*transcript.txt` download only.
  const getRawTextTranscript = () => {
    return transcript.map(item => item.text).join('\n');
  };

  // Compile full structural markdown asset
  const handleMarkdownDownload = () => {
    const markdownContent = `## ${videoInfo.title}

> YouTube URL: ${url}

---

### Description: 

${videoInfo.description}

---

### Transcript: 

${transcript.map(item => `**[${item.timestamp}]** ${item.text}`).join('\n\n')}`;

    const filename = getCleanFileName(videoInfo.title, videoInfo.id, '', 'md');
    downloadFile(markdownContent, filename, 'text/markdown');
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>🎙️ Free YouTube Transcript Generator</h1>
        <p>Get accurate transcripts with timestamps instantly.</p>
      </header>

      <main className="main-content">
        <form onSubmit={fetchTranscript} className="search-form">
          <input
            type="text"
            placeholder="Paste YouTube Video URL here..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Generating...' : 'Get Transcript'}
          </button>
        </form>

        {error && <div className="error-message">⚠️ {error}</div>}

        {transcript.length > 0 && (
          <div className="results-wrapper">

            {/* Main Export Option */}
            <div className="global-actions">
              <button className="btn btn-markdown" onClick={handleMarkdownDownload}>
                📥 Download Full Report (.md)
              </button>
            </div>

            {/* Video Title Card */}
            <div className="meta-card">
              <div className="card-header">
                <h2 className="video-title">🎬 {videoInfo.title}</h2>
                <button className="btn-inline" onClick={() => copyToClipboard(videoInfo.title)}>📋 Copy Title</button>
              </div>

              {/* Description Segment */}
              <div className="description-section">
                <div className="section-title-bar">
                  <h3>Description</h3>
                  <div className="action-group">
                    <button className="btn-inline" onClick={() => copyToClipboard(videoInfo.description)}>📋 Copy</button>
                    <button
                      className="btn-inline"
                      onClick={() => downloadFile(
                        videoInfo.description,
                        getCleanFileName(videoInfo.title, videoInfo.id, 'description', 'txt'),
                        'text/plain'
                      )}
                    >
                      📥 Download .txt
                    </button>
                  </div>
                </div>
                <details className="video-description" open>
                  <summary>Toggle Layout View</summary>
                  <p>{videoInfo.description}</p>
                </details>
              </div>
            </div>

            {/* Transcript Container Segment */}
            <div className="transcript-box">
              <div className="section-title-bar">
                <h2>Transcript Results</h2>
                <div className="action-group">
                  {/* Keeps timestamps when copying to clipboard */}
                  <button className="btn-inline" onClick={() => copyToClipboard(getPlainTextTranscript())}>📋 Copy Full</button>

                  {/* NEW: Downloads ONLY the text without timestamps */}
                  <button
                    className="btn-inline"
                    onClick={() => downloadFile(
                      getRawTextTranscript(), // <--- Swapped to raw text helper
                      getCleanFileName(videoInfo.title, videoInfo.id, 'transcript', 'txt'),
                      'text/plain'
                    )}
                  >
                    📥 Download (excluding timestamp) .txt
                  </button>
                </div>
              </div>

              <div className="transcript-list">
                {transcript.map((item, index) => (
                  <div key={index} className="transcript-item">
                    <span className="timestamp">[{item.timestamp}]</span>
                    <span className="text">{item.text}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        )
        }
      </main >
    </div >
  );
}

export default App;