import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useCalendarEvents } from '@/api/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Loading';
import { Calendar as CalendarIcon, ArrowLeft, BookOpen, Award, Layers, Flag } from 'lucide-react';
import './CalendarPage.css';

export default function CalendarPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();

  const { data: events, isLoading } = useCalendarEvents(courseId);

  if (isLoading) {
    return (
      <div className="cf-calendar-container">
        <Skeleton height="300px" width="100%" />
      </div>
    );
  }

  const getEventIcon = (type) => {
    switch (type) {
      case 'lesson': return <BookOpen size={16} className="cf-ev-icon cf-ev-lesson" />;
      case 'quiz': return <Award size={16} className="cf-ev-icon cf-ev-quiz" />;
      case 'flashcards': return <Layers size={16} className="cf-ev-icon cf-ev-flashcards" />;
      default: return <Flag size={16} className="cf-ev-icon cf-ev-deadline" />;
    }
  };

  return (
    <div className="cf-calendar-container">
      <div className="cf-cal-header">
        <Button variant="ghost" icon={ArrowLeft} onClick={() => navigate(-1)}>
          Back to Planner
        </Button>
        <h1 className="cf-cal-title">Course Learning Timeline & Calendar</h1>
      </div>

      <div className="cf-cal-events-list">
        {events?.map((ev) => (
          <Card key={ev.id} className="cf-cal-event-card">
            <div className="cf-cal-event-left">
              {getEventIcon(ev.event_type)}
              <div>
                <h4 className="cf-cal-event-title">{ev.title}</h4>
                <span className="cf-cal-event-date">{ev.date} • {ev.event_type.toUpperCase()}</span>
              </div>
            </div>
            <span className={`cf-cal-status-badge cf-cal-status--${ev.status}`}>{ev.status}</span>
          </Card>
        ))}
      </div>
    </div>
  );
}
