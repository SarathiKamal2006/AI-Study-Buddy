import React from 'react';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="brand">
        <span style={{ fontSize: '2.2rem' }}>📚</span>
        <div>
          <h1 className="brand-logo">AI Study Buddy</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            RAG-powered PDF Summarizer, Quiz Generator & Q&A Assistant
          </p>
        </div>
      </div>
      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <span className="brand-badge">React 18</span>
        <span className="brand-badge" style={{ background: 'rgba(16, 185, 129, 0.15)', borderColor: 'rgba(16, 185, 129, 0.3)', color: '#34D399' }}>FastAPI</span>
        <span className="brand-badge" style={{ background: 'rgba(168, 85, 247, 0.15)', borderColor: 'rgba(168, 85, 247, 0.3)', color: '#C084FC' }}>Gemini 1.5</span>
      </div>
    </nav>
  );
}
