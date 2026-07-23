import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/store/useAuthStore';
import { authApi } from '@/api/services';
import { useNotificationStore } from '@/store/useNotificationStore';
import { extractApiError } from '@/utils/errorUtils';

export default function RegisterPage() {
  const login = useAuthStore(state => state.login);
  const addNotification = useNotificationStore(state => state.addNotification);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({ full_name: '', email: '', password: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (loading) return;
    setLoading(true);
    try {
      // 1. Register the user
      await authApi.register(formData);
      // 2. Automatically log them in after registration
      const data = await authApi.login({ email: formData.email, password: formData.password });
      login(data.user, data.access_token);
      navigate('/dashboard');
    } catch (error) {
      addNotification({
        title: 'Registration failed',
        message: extractApiError(error),
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: 'var(--space-4)' }}>
      <Card style={{ width: '100%', maxWidth: 400, padding: 'var(--space-8)' }}>
        <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-6)', textAlign: 'center' }}>Create an account</h2>
        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <Input 
            label="Full Name" 
            name="full_name"
            placeholder="Jane Doe" 
            value={formData.full_name}
            onChange={handleChange}
            required 
          />
          <Input 
            label="Email address" 
            name="email"
            type="email" 
            placeholder="name@example.com" 
            value={formData.email}
            onChange={handleChange}
            required 
          />
          <Input 
            label="Password" 
            name="password"
            type="password" 
            value={formData.password}
            onChange={handleChange}
            minLength={8}
            required 
          />
          <Button type="submit" size="lg" isLoading={loading} style={{ marginTop: 'var(--space-2)' }}>
            Create account
          </Button>
        </form>
        <p className="text-body-sm text-secondary" style={{ marginTop: 'var(--space-6)', textAlign: 'center' }}>
          Already have an account? <Link to="/login" className="text-brand">Log in</Link>
        </p>
      </Card>
    </div>
  );
}
