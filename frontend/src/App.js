import React, { useState } from 'react';
import './App.css';

function App() {
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [quizData, setQuizData] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  React.useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const isProduction = process.env.NODE_ENV === 'production';
      const apiUrl = isProduction ? '/api/quizzes' : 'http://localhost:8000/quizzes';
      const response = await fetch(apiUrl);
      if (response.ok) {
        const data = await response.json();
        setHistory(data);
      }
    } catch (err) {
      console.error("Failed to fetch history:", err);
    }
  };

  const loadQuizFromHistory = (quiz) => {
    setQuizData(quiz);
    setUserAnswers(quiz.user_answers || {});
    setShowResults(!!quiz.user_answers && Object.keys(quiz.user_answers).length > 0);
    setShowHistory(false);
    setError(null);
  };

  const deleteQuiz = async (e, quizId) => {
    e.stopPropagation(); // Prevent loading the quiz
    if (!window.confirm("Are you sure you want to delete this quiz?")) return;

    try {
      const isProduction = process.env.NODE_ENV === 'production';
      const apiUrl = isProduction ? `/api/quiz/${quizId}` : `http://localhost:8000/quiz/${quizId}`;

      const response = await fetch(apiUrl, { method: 'DELETE' });

      if (response.ok) {
        setHistory(history.filter(q => q.id !== quizId));
      } else {
        alert("Failed to delete quiz");
      }
    } catch (err) {
      console.error("Error deleting quiz:", err);
      alert("Error deleting quiz");
    }
  };

  const handleGenerate = async () => {
    if (!inputValue.trim()) {
      setError('Please enter a Topic or Wikipedia URL');
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
        body: JSON.stringify(
          inputValue.includes('wikipedia.org')
            ? { url: inputValue }
            : { topic: inputValue }
        ),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to generate quiz. Please check the URL and try again.');
      }

      const data = await response.json();
      setQuizData(data);
      fetchHistory(); // Refresh history after generating new quiz
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

  const handleSaveQuiz = async () => {
    if (!quizData || !quizData.id) return;

    try {
      const isProduction = process.env.NODE_ENV === 'production';
      const apiUrl = isProduction ? `/api/quiz/${quizData.id}/save-results` : `http://localhost:8000/quiz/${quizData.id}/save-results`;

      const response = await fetch(apiUrl, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_answers: userAnswers }),
      });

      if (response.ok) {
        alert('Quiz results saved successfully!');
        fetchHistory(); // Refresh history to show saved status
      } else {
        alert('Failed to save quiz results');
      }
    } catch (err) {
      console.error('Error saving quiz:', err);
      alert('Error saving quiz results');
    }
  };

  const resetQuiz = () => {
    setInputValue('');
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
        <button className="history-toggle-btn" onClick={() => setShowHistory(!showHistory)}>
          {showHistory ? 'Close History' : 'View History'}
        </button>
      </header>

      <main className="App-main">
        {showHistory ? (
          <div className="history-container">
            <h2>Quiz History</h2>
            {history.length === 0 ? (
              <p>No quizzes generated yet.</p>
            ) : (
              <div className="history-list">
                {history.map((quiz) => (
                  <div key={quiz.id} className="history-card" onClick={() => loadQuizFromHistory(quiz)}>
                    <div className="history-card-header">
                      <h3>{quiz.title || quiz.url}</h3>
                      <button
                        className="delete-history-btn"
                        onClick={(e) => deleteQuiz(e, quiz.id)}
                        title="Delete Quiz"
                      >
                        ×
                      </button>
                    </div>
                    <p>{new Date(quiz.created_at).toLocaleDateString()}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : !quizData ? (
          <div className="input-section">


            <input
              type="text"
              placeholder="Enter a Topic or Paste Wikipedia URL..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
              className="url-input"
            />
            <button
              onClick={handleGenerate}
              disabled={loading || !inputValue}
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
