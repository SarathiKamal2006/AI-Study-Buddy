import React, { useState } from 'react';
import { API_BASE } from '../api';

export default function QASection({ docId }) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [chunks, setChunks] = useState([]);
  const [showChunks, setShowChunks] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE}/api/qa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId, query: query.trim() })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to answer question');

      setAnswer(data.answer);
      setChunks(data.chunks || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-card">
      <h2>🔍 Ask Questions (RAG Q&A)</h2>
      <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
        Ask targeted questions about your uploaded document. The RAG vector system retrieves relevant document context and answers precisely.
      </p>

      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <input
          type="text"
          className="input-text"
          placeholder="e.g. What are the key concepts explained in chapter 2?"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="btn btn-primary" disabled={isLoading || !query.trim()}>
          {isLoading ? <><div className="spinner"></div> Searching...</> : 'Get Answer'}
        </button>
      </form>

      {error && (
        <div style={{ color: 'var(--error)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem' }}>
          {error}
        </div>
      )}

      {answer && !isLoading && (
        <div>
          <div style={{
            background: 'rgba(15, 23, 42, 0.7)',
            border: '1px solid var(--border-glow)',
            borderRadius: 'var(--radius-md)',
            padding: '1.5rem',
            marginBottom: '1.5rem'
          }}>
            <h3 style={{ color: '#818CF8', marginBottom: '0.75rem' }}>Answer:</h3>
            <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.7' }}>{answer}</p>
          </div>

          {chunks.length > 0 && (
            <div>
              <button 
                className="btn btn-secondary" 
                style={{ fontSize: '0.85rem' }} 
                onClick={() => setShowChunks(!showChunks)}
              >
                {showChunks ? '📄 Hide Document Chunks' : `📄 View ${chunks.length} Retrieved Source Chunks`}
              </button>

              {showChunks && (
                <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {chunks.map((chunk, idx) => (
                    <div key={idx} style={{
                      background: 'rgba(30, 41, 59, 0.5)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-md)',
                      padding: '1rem',
                      fontSize: '0.9rem',
                      color: 'var(--text-muted)'
                    }}>
                      <strong style={{ color: '#818CF8' }}>Chunk {idx + 1}:</strong>
                      <p style={{ marginTop: '0.25rem', whiteSpace: 'pre-wrap' }}>{chunk}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
