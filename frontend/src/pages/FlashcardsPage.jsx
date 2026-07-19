import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useFlashcards, useReviewFlashcard } from '@/api/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Loading';
import { MarkdownViewer } from '@/components/ui/MarkdownViewer';
import {
  RotateCw,
  Shuffle,
  Clock,
  CheckCircle,
  ArrowLeft,
  Sparkles,
  Layers,
} from 'lucide-react';
import './FlashcardsPage.css';

export default function FlashcardsPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();

  const [mode, setMode] = useState('all');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const { data: deck, isLoading, isError } = useFlashcards(courseId, null, mode);
  const reviewCard = useReviewFlashcard();

  const currentCard = deck?.[currentIndex];

  const handleReview = async (rating) => {
    if (!currentCard || reviewCard.isPending) return;

    try {
      await reviewCard.mutateAsync({
        flashcardId: currentCard.id,
        rating,
      });

      setIsFlipped(false);
      if (currentIndex < (deck?.length || 1) - 1) {
        setCurrentIndex((prev) => prev + 1);
      } else {
        setCurrentIndex(0);
      }
    } catch (err) {
      console.error('Failed to submit review:', err);
    }
  };

  if (isLoading) {
    return (
      <div className="cf-flashcards-container">
        <Skeleton height="300px" width="100%" />
      </div>
    );
  }

  return (
    <div className="cf-flashcards-container">
      <div className="cf-fc-header">
        <Button variant="ghost" icon={ArrowLeft} onClick={() => navigate(-1)}>
          Back to Course
        </Button>
        <div className="cf-fc-title-group">
          <h1 className="cf-fc-title">Flashcard Recall</h1>
          <p className="cf-fc-sub">Active recall powered by SuperMemo SM-2 spaced repetition.</p>
        </div>
      </div>

      {/* Mode Selector Tabs */}
      <div className="cf-mode-tabs">
        {[
          { id: 'all', label: 'All Cards', icon: Layers },
          { id: 'due_today', label: 'Due Today', icon: Clock },
          { id: 'shuffle', label: 'Shuffle', icon: Shuffle },
          { id: 'weak_topics', label: 'Weak Topics', icon: Sparkles },
        ].map((m) => {
          const Icon = m.icon;
          return (
            <button
              key={m.id}
              className={`cf-mode-tab ${mode === m.id ? 'cf-mode-tab--active' : ''}`}
              onClick={() => {
                setMode(m.id);
                setCurrentIndex(0);
                setIsFlipped(false);
              }}
            >
              <Icon size={14} /> {m.label}
            </button>
          );
        })}
      </div>

      {!deck || deck.length === 0 ? (
        <Card className="cf-empty-deck-card">
          <Layers size={48} className="text-secondary" />
          <h3>No Flashcards Found</h3>
          <p>No cards available for this mode yet. Try switching to "All Cards".</p>
          <Button onClick={() => setMode('all')}>View All Cards</Button>
        </Card>
      ) : (
        <>
          {/* Card Counter */}
          <div className="cf-fc-counter">
            Card {currentIndex + 1} of {deck.length}
          </div>

          {/* 3D Flip Card Element */}
          <div
            className={`cf-fc-perspective ${isFlipped ? 'cf-fc--flipped' : ''}`}
            onClick={() => setIsFlipped(!isFlipped)}
          >
            <div className="cf-fc-card">
              {/* Front Side */}
              <div className="cf-fc-face cf-fc-front">
                <div className="cf-fc-badge">Concept / Term</div>
                <div className="cf-fc-content">
                  <MarkdownViewer content={currentCard?.front} />
                </div>
                <div className="cf-fc-hint">Click card to flip and reveal answer</div>
              </div>

              {/* Back Side */}
              <div className="cf-fc-face cf-fc-back">
                <div className="cf-fc-badge cf-badge-back">Explanation / Answer</div>
                <div className="cf-fc-content">
                  <MarkdownViewer content={currentCard?.back} />
                </div>
                <div className="cf-fc-hint">Select your confidence rating below</div>
              </div>
            </div>
          </div>

          {/* SM-2 Self-Rating Actions (Shown after flipping) */}
          {isFlipped && (
            <div className="cf-rating-actions">
              <button
                className="cf-rating-btn cf-rating-again"
                onClick={(e) => {
                  e.stopPropagation();
                  handleReview('again');
                }}
              >
                Again
                <span className="cf-rating-sub">&lt; 1 min</span>
              </button>

              <button
                className="cf-rating-btn cf-rating-hard"
                onClick={(e) => {
                  e.stopPropagation();
                  handleReview('hard');
                }}
              >
                Hard
                <span className="cf-rating-sub">1 day</span>
              </button>

              <button
                className="cf-rating-btn cf-rating-good"
                onClick={(e) => {
                  e.stopPropagation();
                  handleReview('good');
                }}
              >
                Good
                <span className="cf-rating-sub">3 days</span>
              </button>

              <button
                className="cf-rating-btn cf-rating-easy"
                onClick={(e) => {
                  e.stopPropagation();
                  handleReview('easy');
                }}
              >
                Easy
                <span className="cf-rating-sub">6 days</span>
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
