import React from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Send } from 'lucide-react';

export default function ChatPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - var(--topbar-height) - var(--space-16))' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: 'var(--space-4)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)' }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: 'var(--space-8)' }}>
          Start chatting with your AI tutor about the course material.
        </div>
      </div>
      <div style={{ display: 'flex', gap: 'var(--space-2)' }}>
        <Input placeholder="Ask a question..." style={{ flex: 1 }} />
        <Button icon={Send}>Send</Button>
      </div>
    </div>
  );
}
