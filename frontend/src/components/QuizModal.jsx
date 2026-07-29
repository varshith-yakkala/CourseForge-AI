import React, { useState, useEffect } from 'react';
import { X, HelpCircle, CheckCircle, XCircle, RotateCcw, Award, Clock } from 'lucide-react';
import { quizzesApi } from '../api/services';

export function QuizModal({ isOpen, onClose, courseId, lessonId, lessonTitle }) {
  const [step, setStep] = useState('config'); // 'config', 'taking', 'results', 'history'
  const [numQuestions, setNumQuestions] = useState(10);
  const [difficulty, setDifficulty] = useState('Intermediate');
  const [quizData, setQuizData] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [attempts, setAttempts] = useState([]);

  const handleStartQuiz = async () => {
    setLoading(true);
    try {
      const data = await quizzesApi.getQuiz(courseId, lessonId, difficulty, numQuestions);
      setQuizData(data);
      setUserAnswers({});
      setStep('taking');
    } catch (err) {
      console.error("Failed to load quiz:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!quizData) return;
    setLoading(true);
    try {
      const res = await quizzesApi.submitAttempt(quizData.quiz_id, {
        answers: userAnswers,
        difficulty,
        time_taken_sec: 120,
      });
      setResults(res);
      setStep('results');
    } catch (err) {
      console.error("Failed to submit quiz attempt:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFetchHistory = async () => {
    if (!quizData) return;
    try {
      const res = await quizzesApi.getAttempts(quizData.quiz_id);
      setAttempts(res.attempts || []);
      setStep('history');
    } catch (err) {
      console.error("Failed to fetch attempts:", err);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(4px)',
      zIndex: 2000, display: 'flex', justifyContent: 'center', alignItems: 'center',
    }}>
      <div style={{
        background: '#0f172a', border: '1px solid #334155', borderRadius: '12px',
        width: '90%', maxWidth: '700px', maxHeight: '90vh', display: 'flex', flexDirection: 'column',
        boxShadow: '0 20px 50px rgba(0,0,0,0.6)', color: '#f8fafc', overflow: 'hidden',
      }}>
        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <HelpCircle style={{ color: '#38bdf8', width: '22px', height: '22px' }} />
            <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Quiz: {lessonTitle}</h3>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
            <X style={{ width: '22px', height: '22px' }} />
          </button>
        </div>

        {/* Body */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px' }}>
          {step === 'config' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Difficulty Level</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#fff' }}
                >
                  <option value="Beginner">Beginner</option>
                  <option value="Intermediate">Intermediate</option>
                  <option value="Advanced">Advanced</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 600 }}>Number of Questions</label>
                <select
                  value={numQuestions}
                  onChange={(e) => setNumQuestions(Number(e.target.value))}
                  style={{ width: '100%', padding: '10px', borderRadius: '6px', background: '#1e293b', border: '1px solid #334155', color: '#fff' }}
                >
                  <option value={5}>5 Questions</option>
                  <option value={10}>10 Questions</option>
                  <option value={15}>15 Questions</option>
                </select>
              </div>

              <button
                onClick={handleStartQuiz}
                disabled={loading}
                style={{
                  padding: '12px', borderRadius: '8px', border: 'none', background: '#38bdf8',
                  color: '#0f172a', fontWeight: 700, fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer', marginTop: '10px',
                }}
              >
                {loading ? 'Generating Quiz...' : 'Start Quiz'}
              </button>
            </div>
          )}

          {step === 'taking' && quizData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              {quizData.questions.map((q, idx) => (
                <div key={q.id} style={{ background: '#1e293b', padding: '16px', borderRadius: '8px', border: '1px solid #334155' }}>
                  <div style={{ fontWeight: 600, marginBottom: '12px' }}>
                    Q{idx + 1}. {q.question_text}
                  </div>

                  {/* MCQ or True/False options */}
                  {q.options && q.options.length > 0 ? (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {q.options.map((opt, oIdx) => (
                        <label key={oIdx} style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontSize: '0.9rem' }}>
                          <input
                            type="radio"
                            name={`q_${q.id}`}
                            value={opt}
                            checked={userAnswers[q.id] === opt}
                            onChange={(e) => setUserAnswers({ ...userAnswers, [q.id]: e.target.value })}
                          />
                          <span>{opt}</span>
                        </label>
                      ))}
                    </div>
                  ) : (
                    /* Short answer / Fill in blank input */
                    <input
                      type="text"
                      placeholder="Type your answer..."
                      value={userAnswers[q.id] || ''}
                      onChange={(e) => setUserAnswers({ ...userAnswers, [q.id]: e.target.value })}
                      style={{ width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #334155', background: '#0f172a', color: '#fff' }}
                    />
                  )}
                </div>
              ))}

              <button
                onClick={handleSubmit}
                disabled={loading}
                style={{
                  padding: '12px', borderRadius: '8px', border: 'none', background: '#22c55e',
                  color: '#fff', fontWeight: 700, fontSize: '1rem', cursor: loading ? 'not-allowed' : 'pointer',
                }}
              >
                {loading ? 'Grading Quiz...' : 'Submit Quiz'}
              </button>
            </div>
          )}

          {step === 'results' && results && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div style={{
                textAlign: 'center', padding: '20px', borderRadius: '8px',
                background: results.passed ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                border: results.passed ? '1px solid #22c55e' : '1px solid #ef4444',
              }}>
                <Award style={{ width: '40px', height: '40px', color: results.passed ? '#22c55e' : '#ef4444', marginBottom: '8px' }} />
                <h2 style={{ margin: '0 0 6px 0', fontSize: '1.8rem' }}>{results.score_pct}% Score</h2>
                <p style={{ margin: 0, fontWeight: 600, color: results.passed ? '#22c55e' : '#ef4444' }}>
                  {results.passed ? 'PASSED!' : 'NEEDS PRACTICE'}
                </p>
                <span style={{ fontSize: '0.85rem', opacity: 0.8 }}>
                  Correct: {results.correct_count} / {results.total_questions} (Attempt #{results.attempt_number})
                </span>
              </div>

              {/* Question Breakdown */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <h4 style={{ margin: 0 }}>Detailed Answer Breakdown</h4>
                {results.breakdown.map((item, idx) => (
                  <div key={idx} style={{
                    background: '#1e293b', padding: '14px', borderRadius: '8px',
                    borderLeft: item.is_correct ? '4px solid #22c55e' : '4px solid #ef4444',
                  }}>
                    <div style={{ fontWeight: 600, marginBottom: '6px' }}>Q: {item.question_text}</div>
                    <div style={{ fontSize: '0.85rem', color: item.is_correct ? '#4ade80' : '#f87171' }}>
                      Your Answer: {item.user_answer || '(No answer provided)'}
                    </div>
                    {!item.is_correct && (
                      <div style={{ fontSize: '0.85rem', color: '#38bdf8', marginTop: '2px' }}>
                        Correct Answer: {item.correct_answer}
                      </div>
                    )}
                    {item.explanation && (
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8', fontStyle: 'italic', marginTop: '6px' }}>
                        Explanation: {item.explanation}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => setStep('config')}
                  style={{
                    flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #38bdf8',
                    background: 'transparent', color: '#38bdf8', fontWeight: 600, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '6px',
                  }}
                >
                  <RotateCcw style={{ width: '16px', height: '16px' }} /> Retry Quiz
                </button>
                <button
                  onClick={handleFetchHistory}
                  style={{
                    flex: 1, padding: '10px', borderRadius: '6px', border: '1px solid #334155',
                    background: '#1e293b', color: '#fff', fontWeight: 600, cursor: 'pointer',
                  }}
                >
                  View Attempt History
                </button>
              </div>
            </div>
          )}

          {step === 'history' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <h4 style={{ margin: '0 0 10px 0' }}>Previous Quiz Attempts</h4>
              {attempts.length === 0 && <div style={{ color: '#64748b' }}>No previous attempts found.</div>}
              {attempts.map((a) => (
                <div key={a.attempt_id} style={{
                  background: '#1e293b', padding: '12px 16px', borderRadius: '8px', border: '1px solid #334155',
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                }}>
                  <div>
                    <div style={{ fontWeight: 600, color: a.passed ? '#4ade80' : '#f87171' }}>
                      Attempt #{a.attempt_number} — {a.score_pct}% ({a.passed ? 'PASSED' : 'FAILED'})
                    </div>
                    <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                      {a.submitted_at ? new Date(a.submitted_at).toLocaleString() : ''}
                    </span>
                  </div>
                  <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                    <Clock style={{ width: '14px', height: '14px', display: 'inline', marginRight: '4px' }} />
                    {a.time_taken_sec}s
                  </span>
                </div>
              ))}
              <button
                onClick={() => setStep('config')}
                style={{ padding: '8px 16px', borderRadius: '6px', background: '#38bdf8', border: 'none', color: '#0f172a', fontWeight: 600, cursor: 'pointer', marginTop: '10px' }}
              >
                Back to Quiz Config
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
