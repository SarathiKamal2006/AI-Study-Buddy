import React, { useState } from 'react';

export default function QuizEngine({ docId }) {
  const [quiz, setQuiz] = useState(null);
  const [quizText, setQuizText] = useState('');
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchQuiz = async () => {
    setIsLoading(true);
    setError('');
    setSelectedAnswers({});
    setShowResults(false);

    try {
      const response = await fetch('/api/quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ doc_id: docId })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to generate quiz');

      if (data.quiz) {
        setQuiz(data.quiz);
        setQuizText('');
      } else if (data.quiz_text) {
        setQuizText(data.quiz_text);
        setQuiz(null);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectOption = (questionId, optionKey) => {
    if (showResults) return;
    setSelectedAnswers(prev => ({
      ...prev,
      [questionId]: optionKey
    }));
  };

  const calculateScore = () => {
    if (!quiz) return 0;
    let score = 0;
    quiz.forEach(q => {
      if (selectedAnswers[q.id] === q.answer) {
        score += 1;
      }
    });
    return score;
  };

  return (
    <div className="glass-card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2>❓ Interactive MCQ Practice Quiz</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
            Test your comprehension with automatically generated practice questions.
          </p>
        </div>
        {(!quiz && !quizText) && (
          <button className="btn btn-primary" onClick={fetchQuiz} disabled={isLoading}>
            {isLoading ? <><div className="spinner"></div> Generating...</> : '🎯 Generate Quiz'}
          </button>
        )}
      </div>

      {isLoading && (
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="spinner" style={{ margin: '0 auto 1rem auto' }}></div>
          <p style={{ color: 'var(--text-muted)' }}>Creating custom 10 MCQ practice questions with Gemini AI...</p>
        </div>
      )}

      {error && (
        <div style={{ color: 'var(--error)', padding: '1rem', background: 'rgba(239,68,68,0.1)', borderRadius: 'var(--radius-md)' }}>
          {error}
        </div>
      )}

      {quiz && !isLoading && (
        <div>
          {quiz.map((q, idx) => (
            <div key={q.id || idx} className="quiz-card">
              <h3 style={{ marginBottom: '1rem' }}>
                Question {idx + 1}: {q.question}
              </h3>
              <div>
                {Object.entries(q.options).map(([key, val]) => {
                  const isSelected = selectedAnswers[q.id] === key;
                  const isCorrect = q.answer === key;
                  let optionClass = 'option-btn';

                  if (showResults) {
                    if (isCorrect) optionClass += ' correct';
                    else if (isSelected) optionClass += ' wrong';
                  } else if (isSelected) {
                    optionClass += ' correct';
                  }

                  return (
                    <button
                      key={key}
                      className={optionClass}
                      onClick={() => handleSelectOption(q.id, key)}
                    >
                      <strong style={{ marginRight: '0.75rem', width: '24px' }}>{key})</strong>
                      <span>{val}</span>
                    </button>
                  );
                })}
              </div>
            </div>
          ))}

          <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            {!showResults ? (
              <button 
                className="btn btn-primary" 
                onClick={() => setShowResults(true)}
                disabled={Object.keys(selectedAnswers).length === 0}
              >
                Submit Answers & Check Score
              </button>
            ) : (
              <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div style={{ fontSize: '1.2rem', fontWeight: '700', color: '#34D399' }}>
                  🏆 Score: {calculateScore()} / {quiz.length} ({Math.round((calculateScore() / quiz.length) * 100)}%)
                </div>
                <button className="btn btn-secondary" onClick={fetchQuiz}>
                  🔄 Retake New Quiz
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {quizText && !isLoading && (
        <div>
          <div style={{ 
            background: 'rgba(15, 23, 42, 0.6)', 
            padding: '1.5rem', 
            borderRadius: 'var(--radius-md)', 
            whiteSpace: 'pre-wrap',
            marginBottom: '1.5rem' 
          }}>
            {quizText}
          </div>
          <button className="btn btn-secondary" onClick={fetchQuiz}>
            🔄 Regenerate Quiz
          </button>
        </div>
      )}
    </div>
  );
}
