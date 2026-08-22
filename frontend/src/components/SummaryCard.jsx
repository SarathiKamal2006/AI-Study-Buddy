import React, { useState } from 'react';
import { API_BASE } from '../api';

export default function SummaryCard({ docId }) {
  const [summary, setSummary] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState('');

  const fetchSummary = async () => {
    setIsLoading(true);
    setError('');
    try {
      const response = await fetch(`${API_BASE}/api/summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to generate summary');
      setSummary(data.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <h2>📝 Document Summary</h2>
        {!summary && (
          <button className="btn btn-primary" onClick={fetchSummary} disabled={isLoading}>
            {isLoading ? <><div className="spinner"></div> Generating...</> : '✨ Generate Summary'}
          </button>
        )}
      </div>

      {isLoading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem auto' }}></div>
          <p style={{ color: 'var(--text-muted)' }}>Summarizing document key concepts with Gemini AI...</p>
        </div>
      )}

      {error && (
        <div style={{ color: 'var(--error)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {summary && !isLoading && (
        <div>
          <div style={{ 
            background: 'rgba(15, 23, 42, 0.6)', 
            padding: '1.5rem', 
            borderRadius: 'var(--radius-md)', 
            border: '1px solid var(--border-color)',
            whiteSpace: 'pre-wrap',
            marginBottom: '1.5rem'
          }}>
            {summary}
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            <button className="btn btn-secondary" onClick={handleCopy}>
              {copied ? '✅ Copied!' : '📋 Copy Summary'}
            </button>
            <button className="btn btn-secondary" onClick={fetchSummary}>
              🔄 Regenerate
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
