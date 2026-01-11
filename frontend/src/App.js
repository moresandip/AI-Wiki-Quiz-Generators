import React, { useState } from 'react';
import './App.css';

function App() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [quizData, setQuizData] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!url) {
      setError('Please enter a Wikipedia URL');
      return;
    }

    setLoading(true);
    setError(null);
    setQuizData(null);
    setUserAnswers({});
    setShowResults(false);

    const isProduction = process.env.NODE_ENV === 'production';
    const apiUrl = isProduction ? '/api/generate-quiz' : 'http://localhost:8000/generate-quiz';

    try {
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to generate quiz. Please check the URL and try again.');
      }

      const data = await response.json();
      setQuizData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionIndex, option) => {
    if (showResults) return; // Prevent changing answers after submission
    setUserAnswers(prev => ({
      ...prev,
      [questionIndex]: option
    }));
  };

  const calculateScore = () => {
    if (!quizData || !quizData.data || !quizData.data.quiz) return 0;
    let score = 0;
    quizData.data.quiz.forEach((q, index) => {
      if (userAnswers[index] === q.answer) {
        score++;
      }
    });
    return score;
  };

  const handleSubmit = () => {
    setShowResults(true);
  };

  const resetQuiz = () => {
    setUrl('');
    setQuizData(null);
    setUserAnswers({});
    setShowResults(false);
    setError(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Wiki Quiz Generator</h1>
        <p>Turn any Wikipedia article into an interactive quiz instantly.</p>
      </header>

      <main className="App-main">
        {!quizData ? (
          <div className="input-section">
            <input
              type="text"
              placeholder="Paste Wikipedia URL here..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              disabled={loading}
              className="url-input"
            />
            <button
              onClick={handleGenerate}
              disabled={loading || !url}
              className="generate-btn"
            >
              {loading ? 'Generating Quiz...' : 'Generate Quiz'}
            </button>
            {error && <div className="error-message">{error}</div>}
            {loading && (
              <div className="loading-indicator">
                <div className="spinner"></div>
                <p>Analyzing article and generating questions...</p>
              </div>
            )}
          </div>
        ) : (
          <div className="quiz-container">
            <div className="quiz-header">
              <h2>{quizData.title}</h2>
              <p className="quiz-summary">{quizData.summary}</p>
              <button onClick={resetQuiz} className="reset-btn">Create New Quiz</button>
            </div>

            <div className="questions-list">
              {quizData.data.quiz.map((q, index) => (
                <div key={index} className={`question-card ${showResults ? (userAnswers[index] === q.answer ? 'correct' : 'incorrect') : ''}`}>
                  <div className="question-header">
                    <span className="question-number">Q{index + 1}</span>
                    <span className={`difficulty-badge ${q.difficulty}`}>{q.difficulty}</span>
                  </div>
                  <h3 className="question-text">{q.question}</h3>
                  <div className="options-grid">
                    {q.options.map((option, optIndex) => (
                      <div
                        key={optIndex}
                        className={`option-item 
                          ${userAnswers[index] === option ? 'selected' : ''} 
                          ${showResults && option === q.answer ? 'correct-answer' : ''}
                          ${showResults && userAnswers[index] === option && option !== q.answer ? 'wrong-answer' : ''}
                        `}
                        onClick={() => handleAnswerSelect(index, option)}
                      >
                        {option}
                      </div>
                    ))}
                  </div>
                  {showResults && (
                    <div className="explanation">
                      <strong>Explanation:</strong> {q.explanation}
                    </div>
                  )}
                </div>
              ))}
            </div>

            {!showResults ? (
              <button
                onClick={handleSubmit}
                className="submit-btn"
                disabled={Object.keys(userAnswers).length !== quizData.data.quiz.length}
              >
                Submit Answers
              </button>
            ) : (
              <div className="results-summary">
                <h3>Quiz Complete!</h3>
                <p className="score-display">
                  You scored <strong>{calculateScore()}</strong> out of <strong>{quizData.data.quiz.length}</strong>
                </p>
                <button onClick={resetQuiz} className="reset-btn large">Try Another Article</button>
              </div>
            )}

            {quizData.data.related_topics && (
              <div className="related-topics">
                <h4>Related Topics:</h4>
                <div className="topics-tags">
                  {quizData.data.related_topics.map((topic, i) => (
                    <span key={i} className="topic-tag">{topic}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
