import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  usePlannerSchedule,
  useUpdatePlannerPlan,
  usePredictions,
  useCourse,
} from '@/api/hooks';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Skeleton } from '@/components/ui/Loading';
import {
  Calendar as CalendarIcon,
  Clock,
  CheckCircle2,
  Sparkles,
  TrendingUp,
  Target,
  ArrowRight,
  BookOpen,
} from 'lucide-react';
import './StudyPlannerPage.css';

export default function StudyPlannerPage() {
  const { courseId } = useParams();
  const navigate = useNavigate();

  const [dailyMins, setDailyMins] = useState(30);

  const { data: course } = useCourse(courseId);
  const { data: schedule, isLoading: isScheduleLoading } = usePlannerSchedule(courseId);
  const { data: predictions } = usePredictions(courseId);

  const updatePlan = useUpdatePlannerPlan();

  const handleUpdatePlan = async (e) => {
    e.preventDefault();
    try {
      await updatePlan.mutateAsync({
        courseId,
        planData: { daily_goal_min: parseInt(dailyMins, 10) },
      });
    } catch (err) {
      console.error('Failed to update plan:', err);
    }
  };

  if (isScheduleLoading) {
    return (
      <div className="cf-planner-container">
        <Skeleton height="40px" width="300px" style={{ marginBottom: '24px' }} />
        <Skeleton height="150px" width="100%" style={{ marginBottom: '24px' }} />
        <Skeleton height="300px" width="100%" />
      </div>
    );
  }

  return (
    <div className="cf-planner-container">
      <div className="cf-planner-header">
        <div>
          <h1 className="cf-planner-title">Adaptive AI Study Planner</h1>
          <p className="cf-planner-sub">Dynamic learning roadmap tailored to your pace for "{course?.title || 'Course'}"</p>
        </div>

        <Button icon={CalendarIcon} variant="outline" onClick={() => navigate(`/calendar/${courseId}`)}>
          View Calendar Timeline
        </Button>
      </div>

      {/* Pace Predictions Gauge Grid */}
      <div className="cf-predictions-grid">
        <Card className="cf-pred-card">
          <div className="cf-pred-header">
            <Target size={18} className="cf-pred-icon text-brand" />
            <span>Estimated Finish Date</span>
          </div>
          <div className="cf-pred-value">{predictions?.estimated_completion_date || 'In 14 Days'}</div>
          <div className="cf-pred-sub">Based on current daily learning velocity</div>
        </Card>

        <Card className="cf-pred-card">
          <div className="cf-pred-header">
            <TrendingUp size={18} className="cf-pred-icon text-success" />
            <span>On-Time Probability</span>
          </div>
          <div className="cf-pred-value">{predictions?.on_time_probability_pct || 85}%</div>
          <div className="cf-pred-sub">Confidence Level: {predictions?.confidence_level || 'High'}</div>
        </Card>

        <Card className="cf-pred-card">
          <div className="cf-pred-header">
            <Clock size={18} className="cf-pred-icon text-warning" />
            <span>Remaining Effort</span>
          </div>
          <div className="cf-pred-value">{schedule?.remaining_hours || 4.5} Hours</div>
          <div className="cf-pred-sub">{schedule?.remaining_uncompleted_lessons || 3} Uncompleted Lessons</div>
        </Card>
      </div>

      {/* Goal Settings Form */}
      <Card className="cf-planner-settings-card">
        <h3 className="cf-settings-title">Study Goal Preferences</h3>
        <form onSubmit={handleUpdatePlan} className="cf-settings-form">
          <div className="cf-form-field">
            <label>Daily Study Goal (Minutes):</label>
            <Input
              type="number"
              value={dailyMins}
              onChange={(e) => setDailyMins(e.target.value)}
              style={{ width: '120px' }}
            />
          </div>

          <Button type="submit" isLoading={updatePlan.isPending}>
            Rebalance Schedule
          </Button>
        </form>
      </Card>

      {/* Adaptive Roadmap Schedule Blocks */}
      <div className="cf-schedule-section">
        <h2 className="cf-section-title">Adaptive Daily Roadmap</h2>
        <div className="cf-blocks-list">
          {schedule?.schedule_blocks?.map((block, idx) => (
            <Card key={idx} className="cf-block-item">
              <div className="cf-block-left">
                <span className="cf-block-date">{block.day_name}</span>
                <h4 className="cf-block-title">{block.title}</h4>
                <span className="cf-block-type">{block.activity_type.toUpperCase()} • {block.estimated_mins} mins</span>
              </div>

              {block.lesson_id && (
                <Button
                  size="sm"
                  variant="outline"
                  icon={ArrowRight}
                  onClick={() => navigate(`/learn/${courseId}/${block.lesson_id}`)}
                >
                  Start Lesson
                </Button>
              )}
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
