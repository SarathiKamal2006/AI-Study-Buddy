import React, { useState } from 'react';

export default function UploadSection({ onUploadSuccess, docInfo, isUploading, setIsUploading }) {
  const [dragOver, setDragOver] = useState(false);
  const [error, setError] = useState('');

  const handleFileChange = async (file) => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Please select a valid PDF file.');
      return;
    }

    setError('');
    setIsUploading(true);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to upload PDF.');
      }

      onUploadSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="glass-card" style={{ marginBottom: '2rem' }}>
      <div 
        className={`upload-zone ${dragOver ? 'dragover' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => document.getElementById('pdf-input').click()}
      >
        <input 
          id="pdf-input" 
          type="file" 
          accept="application/pdf" 
          style={{ display: 'none' }} 
          onChange={(e) => e.target.files && handleFileChange(e.target.files[0])}
        />
        
        {isUploading ? (
          <div>
            <div className="spinner" style={{ margin: '0 auto 1rem auto' }}></div>
            <h3>Extracting text & building RAG vector index...</h3>
            <p style={{ color: 'var(--text-muted)' }}>This usually takes a few seconds.</p>
          </div>
        ) : docInfo ? (
          <div>
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>✅</div>
            <h3 style={{ color: '#34D399' }}>{docInfo.filename}</h3>
            <p style={{ color: 'var(--text-muted)' }}>
              Extracted {docInfo.char_count.toLocaleString()} characters. Ready for AI Study Tools!
            </p>
            <button className="btn btn-secondary" style={{ marginTop: '1rem' }}>
              Click to replace PDF
            </button>
          </div>
        ) : (
          <div>
            <div className="upload-icon">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
              </svg>
            </div>
            <h3>Drag & Drop your PDF study notes here</h3>
            <p style={{ color: 'var(--text-muted)', marginTop: '0.5rem' }}>
              or click to browse from your computer
            </p>
          </div>
        )}
      </div>

      {error && (
        <div style={{ marginTop: '1rem', color: 'var(--error)', padding: '0.75rem', background: 'rgba(239,68,68,0.1)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
