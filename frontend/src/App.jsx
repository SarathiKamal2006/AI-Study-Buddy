import React, { useState } from 'react';
import Navbar from './components/Navbar';
import UploadSection from './components/UploadSection';
import SummaryCard from './components/SummaryCard';
import QuizEngine from './components/QuizEngine';
import QASection from './components/QASection';

export default function App() {
  const [docInfo, setDocInfo] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');

  const handleUploadSuccess = (data) => {
    setDocInfo(data);
    setActiveTab('summary');
  };

  return (
    <div className="container">
      <Navbar />

      <UploadSection 
        onUploadSuccess={handleUploadSuccess} 
        docInfo={docInfo}
        isUploading={isUploading}
        setIsUploading={setIsUploading}
      />

      {docInfo && (
        <div>
          <div className="tabs-nav">
            <button 
              className={`tab-btn ${activeTab === 'summary' ? 'active' : ''}`}
              onClick={() => setActiveTab('summary')}
            >
              📝 Document Summary
            </button>
            <button 
              className={`tab-btn ${activeTab === 'quiz' ? 'active' : ''}`}
              onClick={() => setActiveTab('quiz')}
            >
              ❓ Interactive Quiz
            </button>
            <button 
              className={`tab-btn ${activeTab === 'qa' ? 'active' : ''}`}
              onClick={() => setActiveTab('qa')}
            >
              🔍 RAG Q&A Assistant
            </button>
          </div>

          <div style={{ marginTop: '1.5rem' }}>
            {activeTab === 'summary' && <SummaryCard docId={docInfo.doc_id} />}
            {activeTab === 'quiz' && <QuizEngine docId={docInfo.doc_id} />}
            {activeTab === 'qa' && <QASection docId={docInfo.doc_id} />}
          </div>
        </div>
      )}
    </div>
  );
}
