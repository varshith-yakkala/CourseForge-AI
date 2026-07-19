import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuiz, useSubmitQuiz } from '@/api/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Loading';
import { MarkdownViewer } from '@/components/ui/MarkdownViewer';
import {
  Clock,
  CheckCircle2,
  XCircle,
  HelpCircle,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  Award,
  Sparkles,
  ArrowLeft,
} from 'lucide-react';
import './QuizPage.css';

export default function QuizPage() {
  const { courseId, lessonId } = useParams();
  const navigate = useNavigate();

  const [difficulty, setDifficulty] = useState('Intermediate');
  const [hasStarted, setHasStarted] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(600);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [result, setResult] = useState(null);

  const {
    data: quizData,
    isLoading,
    isError,
    refetch,
  } = useQuiz(courseId, lessonId, difficulty, 10);

  const submitQuiz = useSubmitQuiz();

  // Timer countdown
  useEffect(() => {
    if (!hasStarted || isSubmitted || timeLeft <= 0) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => prev - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [hasStarted, isSubmitted, timeLeft]);

  const questions = quizData?.questions || [];
  const currentQuestion = questions[currentIndex];

  const handleSelectOption = (option) => {
    if (!currentQuestion) return;
    setUserAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: option,
    }));
  };

  const handleTextChange = (val) => {
    if (!currentQuestion) return;
    setUserAnswers((prev) => ({
      ...prev,
      [currentQuestion.id]: val,
    }));
  };

  const handleSubmit = async () => {
    if (!quizData?.quiz_id || submitQuiz.isPending) return;

    try {
      const res = await submitQuiz.mutateAsync({
        quizId: quizData.quiz_id,
        attemptData: {
          answers: userAnswers,
          difficulty,
          time_taken_sec: 600 - timeLeft,
        },
      });
      setResult(res);
      setIsSubmitted(true);
    } catch (err) {
      console.error('Failed to submit quiz:', err);
    }
  };

  const handleStart = (diff) => {
    setDifficulty(diff);
    setHasStarted(true);
    setCurrentIndex(0);
    setUserAnswers({});
    setIsSubmitted(false);
    setResult(null);
    setTimeLeft(600);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  if (isLoading) {
    return (
      <div className="cf-quiz-container">
        <Skeleton height="40px" width="300px" style={{ marginBottom: '24px' }} />
        <Skeleton height="200px" width="100%" />
      </div>
    );
  }

  // Pre-Quiz Difficulty Selector
  if (!hasStarted) {
    return (
      <div className="cf-quiz-container">
        <Button variant="ghost" icon={ArrowLeft} onClick={() => navigate(-1)} style={{ marginBottom: '16px' }}>
          Back to Lesson
        </Button>

        <Card className="cf-quiz-start-card">
          <div className="cf-quiz-badge">
            <Sparkles size={16} /> Interactive Assessment
          </div>
          <h1 className="cf-quiz-start-title">{quizData?.title || 'Lesson Quiz'}</h1>
          <p className="cf-quiz-start-sub">
            Choose your difficulty level. Question pool generates 10 randomized questions with instant scoring & detailed explanations.
          </p>

          <div className="cf-difficulty-grid">
            {['Beginner', 'Intermediate', 'Advanced'].map((lvl) => (
              <div
                key={lvl}
                className={`cf-difficulty-card ${difficulty === lvl ? 'cf-difficulty-card--selected' : ''}`}
                onClick={() => setDifficulty(lvl)}
              >
                <div className="cf-diff-title">{lvl}</div>
                <div className="cf-diff-desc">
                  {lvl === 'Beginner' && 'Core definitions & foundational recall.'}
                  {lvl === 'Intermediate' && 'Conceptual application & code examples.'}
                  {lvl === 'Advanced' && 'Deep synthesis, edge cases & scenarios.'}
                </div>
              </div>
            ))}
          </div>

          <Button size="lg" icon={Sparkles} onClick={() => handleStart(difficulty)}>
            Start {difficulty} Quiz
          </Button>
        </Card>
      </div>
    );
  }

  // Results & Detailed Breakdown View
  if (isSubmitted && result) {
    return (
      <div className="cf-quiz-container">
        <Card className={`cf-quiz-result-card ${result.passed ? 'cf-result--pass' : 'cf-result--fail'}`}>
          <div className="cf-result-header">
            {result.passed ? (
              <CheckCircle2 size={48} className="cf-icon-pass" />
            ) : (
              <XCircle size={48} className="cf-icon-fail" />
            )}
            <h2>{result.passed ? 'Quiz Passed!' : 'Needs Practice'}</h2>
            <div className="cf-result-score-display">{result.score_pct}%</div>
            <p className="cf-result-meta">
              Passed Score Threshold: {quizData?.pass_score_pct}% | Time Taken: {formatTime(result.time_taken_sec)}
            </p>
          </div>

          <div className="cf-result-actions">
            <Button icon={RotateCcw} onClick={() => handleStart(difficulty)}>
              Retake Quiz
            </Button>

            <Button variant="outline" onClick={() => navigate(`/learn/${courseId}/${lessonId}`)}>
              Back to Lesson
            </Button>
          </div>
        </Card>

        {/* Detailed Question Review List */}
        <h3 className="cf-review-heading">Question Breakdown & Explanations</h3>
        <div className="cf-review-list">
          {result.breakdown?.map((item, idx) => (
            <Card key={item.question_id} className={`cf-review-item ${item.is_correct ? 'cf-review--correct' : 'cf-review--incorrect'}`}>
              <div className="cf-review-q-header">
                <span className="cf-review-q-num">Q{idx + 1}.</span>
                <span className="cf-review-q-text">{item.question_text}</span>
                <span className={`cf-review-tag ${item.is_correct ? 'cf-tag-pass' : 'cf-tag-fail'}`}>
                  {item.is_correct ? `+${item.points_earned} pts` : '0 pts'}
                </span>
              </div>

              <div className="cf-review-ans-grid">
                <div>
                  <strong>Your Answer:</strong> {item.user_answer || '(No answer provided)'}
                </div>
                <div>
                  <strong>Correct Answer:</strong> {item.correct_answer}
                </div>
              </div>

              {item.explanation && (
                <div className="cf-review-explanation">
                  <strong>Explanation:</strong> {item.explanation}
                </div>
              )}
            </Card>
          ))}
        </div>
      </div>
    );
  }

  // Interactive Quiz Runner View
  return (
    <div className="cf-quiz-container">
      {/* Top Header bar */}
      <div className="cf-quiz-runner-header">
        <div>
          <span className="cf-quiz-step-tag">
            Question {currentIndex + 1} of {questions.length}
          </span>
          <h2 className="cf-quiz-runner-title">{quizData?.title}</h2>
        </div>

        <div className="cf-quiz-timer">
          <Clock size={16} /> {formatTime(timeLeft)}
        </div>
      </div>

      {/* Progress Bar */}
      <div className="cf-quiz-progress-track">
        <div
          className="cf-quiz-progress-fill"
          style={{ width: `${((currentIndex + 1) / questions.length) * 100}%` }}
        />
      </div>

      {/* Question Card */}
      {currentQuestion && (
        <Card className="cf-question-card">
          <h3 className="cf-question-text">{currentQuestion.question_text}</h3>

          {/* Question Type: Multiple Choice or True/False */}
          {(currentQuestion.question_type === 'multiple_choice' || currentQuestion.question_type === 'true_false') && (
            <div className="cf-options-grid">
              {(currentQuestion.options || ['True', 'False']).map((opt, i) => {
                const isSelected = userAnswers[currentQuestion.id] === opt;
                return (
                  <div
                    key={i}
                    className={`cf-option-item ${isSelected ? 'cf-option-item--selected' : ''}`}
                    onClick={() => handleSelectOption(opt)}
                  >
                    <span className="cf-option-radio">{isSelected ? '●' : '○'}</span>
                    <span className="cf-option-text">{opt}</span>
                  </div>
                );
              })}
            </div>
          )}

          {/* Question Type: Fill in Blank / Short Answer / Code Output */}
          {currentQuestion.question_type !== 'multiple_choice' && currentQuestion.question_type !== 'true_false' && (
            <div className="cf-text-answer-box">
              <Input
                placeholder="Type your answer here..."
                value={userAnswers[currentQuestion.id] || ''}
                onChange={(e) => handleTextChange(e.target.value)}
              />
            </div>
          )}
        </Card>
      )}

      {/* Navigation Footer */}
      <div className="cf-quiz-footer">
        <Button
          variant="outline"
          icon={ChevronLeft}
          disabled={currentIndex === 0}
          onClick={() => setCurrentIndex((prev) => prev - 1)}
        >
          Previous
        </Button>

        {currentIndex < questions.length - 1 ? (
          <Button
            icon={ChevronRight}
            onClick={() => setCurrentIndex((prev) => prev + 1)}
          >
            Next Question
          </Button>
        ) : (
          <Button
            variant="primary"
            icon={CheckCircle2}
            isLoading={submitQuiz.isPending}
            onClick={handleSubmit}
          >
            Submit Quiz
          </Button>
        )}
      </div>
    </div>
  );
}
