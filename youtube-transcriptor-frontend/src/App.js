import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [transcript, setTranscript] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchTranscript = async (e) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    setError('');
    setTranscript([]);

    try {
      const response = await fetch('http://127.0.0.1:8000/transcript', {
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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
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
            placeholder="Paste YouTube Video URL here (e.g., https://www.youtube.com/watch?v=...)"
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
          <div className="transcript-box">
            <h2>Transcript Results</h2>
            <div className="transcript-list">
              {transcript.map((item, index) => (
                <div key={index} className="transcript-item">
                  <span className="timestamp">[{item.timestamp}]</span>
                  <span className="text">{item.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;