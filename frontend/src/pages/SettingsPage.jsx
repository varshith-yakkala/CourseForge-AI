import React from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/store/useAuthStore';

export default function SettingsPage() {
  const user = useAuthStore(state => state.user);
  
  return (
    <div style={{ maxWidth: 600 }}>
      <h1 className="text-heading-lg" style={{ marginBottom: 'var(--space-6)' }}>Settings</h1>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-6)' }}>
        <Input label="Full Name" defaultValue={user?.full_name || ''} />
        <Input label="Email" type="email" defaultValue={user?.email || 'user@example.com'} />
        <Button>Save Changes</Button>
      </div>
    </div>
  );
}
