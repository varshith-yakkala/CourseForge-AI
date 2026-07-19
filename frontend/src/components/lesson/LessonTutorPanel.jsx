import React, { useState } from 'react';
import { X, Send, Bot, User, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { MarkdownViewer } from '@/components/ui/MarkdownViewer';
import { useAskLessonTutor } from '@/api/hooks';
import './LessonTutorPanel.css';

export function LessonTutorPanel({ isOpen, onClose, courseId, lessonId, lessonTitle }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      role: 'assistant',
      content: `Hello! I am your AI Tutor for **"${lessonTitle || 'this lesson'}"**. Ask me anything about the content or concepts covered in this lesson!`,
    },
  ]);

  const askTutor = useAskLessonTutor();

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim() || askTutor.isPending) return;

    const userMsg = { id: Date.now().toString(), role: 'user', content: question.trim() };
    setMessages((prev) => [...prev, userMsg]);
    const currentQ = question.trim();
    setQuestion('');

    try {
      const res = await askTutor.mutateAsync({
        courseId,
        lessonId,
        question: currentQ,
      });

      const aiMsg = { id: (Date.now() + 1).toString(), role: 'assistant', content: res.answer };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errorMsg = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I ran into an issue answering your question. Please try asking again.',
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="cf-tutor-panel-backdrop" onClick={onClose}>
      <div className="cf-tutor-panel" onClick={(e) => e.stopPropagation()}>
        <div className="cf-tutor-panel-header">
          <div className="cf-tutor-title-wrapper">
            <Bot className="cf-tutor-icon" size={20} />
            <div>
              <h3 className="cf-tutor-heading">Ask About This Lesson</h3>
              <p className="cf-tutor-subheading">Scoped AI Assistant for "{lessonTitle}"</p>
            </div>
          </div>
          <button className="cf-tutor-close-btn" onClick={onClose} aria-label="Close panel">
            <X size={18} />
          </button>
        </div>

        <div className="cf-tutor-messages">
          {messages.map((msg) => (
            <div key={msg.id} className={`cf-tutor-msg cf-tutor-msg--${msg.role}`}>
              <div className="cf-tutor-msg-avatar">
                {msg.role === 'assistant' ? <Sparkles size={16} /> : <User size={16} />}
              </div>
              <div className="cf-tutor-msg-body">
                <MarkdownViewer content={msg.content} />
              </div>
            </div>
          ))}
          {askTutor.isPending && (
            <div className="cf-tutor-msg cf-tutor-msg--assistant">
              <div className="cf-tutor-msg-avatar">
                <Sparkles size={16} className="cf-pulse-icon" />
              </div>
              <div className="cf-tutor-msg-body">
                <span className="cf-tutor-thinking">Thinking based on lesson content...</span>
              </div>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="cf-tutor-input-form">
          <Input
            placeholder="Ask a question about this lesson..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={askTutor.isPending}
            style={{ flex: 1 }}
          />
          <Button type="submit" icon={Send} isLoading={askTutor.isPending} disabled={!question.trim()}>
            Send
          </Button>
        </form>
      </div>
    </div>
  );
}
