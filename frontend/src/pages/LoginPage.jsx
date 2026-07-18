import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/store/useAuthStore';
import { authApi } from '@/api/services';
import { useNotificationStore } from '@/store/useNotificationStore';

export default function LoginPage() {
  const login = useAuthStore(state => state.login);
  const addNotification = useNotificationStore(state => state.addNotification);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({ email: '', password: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await authApi.login(formData);
      login(data.user, data.access_token);
      navigate('/dashboard');
    } catch (error) {
      addNotification({
        title: 'Login failed',
        message: error.response?.data?.detail || 'Please check your credentials and try again.',
        type: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: 'var(--space-4)' }}>
      <Card style={{ width: '100%', maxWidth: 400, padding: 'var(--space-8)' }}>
        <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-6)', textAlign: 'center' }}>Log in to your account</h2>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
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
            required 
          />
          <Button type="submit" size="lg" isLoading={loading} style={{ marginTop: 'var(--space-2)' }}>
            Log in
          </Button>
        </form>
        <p className="text-body-sm text-secondary" style={{ marginTop: 'var(--space-6)', textAlign: 'center' }}>
          Don't have an account? <Link to="/register" className="text-brand">Sign up</Link>
        </p>
      </Card>
    </div>
  );
}
