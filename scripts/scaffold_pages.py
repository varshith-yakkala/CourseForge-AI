import os

files = {
    'frontend/src/pages/LandingPage.jsx': '''
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/Button';
import { Footer } from '@/components/layout/Footer';

export default function LandingPage() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 'var(--space-8)', textAlign: 'center' }}>
        <h1 className="text-display-lg" style={{ marginBottom: 'var(--space-4)' }}>CourseForge AI</h1>
        <p className="text-body-xl text-secondary" style={{ maxWidth: 600, marginBottom: 'var(--space-8)' }}>
          Transform any PDF into an interactive learning course with AI.
        </p>
        <div style={{ display: 'flex', gap: 'var(--space-4)' }}>
          <Link to="/register"><Button size="lg">Get Started</Button></Link>
          <Link to="/login"><Button variant="secondary" size="lg">Log In</Button></Link>
        </div>
      </main>
      <Footer />
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/LoginPage.jsx': '''
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/store/useAuthStore';

export default function LoginPage() {
  const login = useAuthStore(state => state.login);
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    login({ id: 1, full_name: 'Demo User' }, 'fake-token');
    navigate('/dashboard');
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: 'var(--space-4)' }}>
      <Card style={{ width: '100%', maxWidth: 400, padding: 'var(--space-8)' }}>
        <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-6)', textAlign: 'center' }}>Log in to your account</h2>
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <Input label="Email address" type="email" placeholder="name@example.com" required />
          <Input label="Password" type="password" required />
          <Button type="submit" size="lg" style={{ marginTop: 'var(--space-2)' }}>Log in</Button>
        </form>
        <p className="text-body-sm text-secondary" style={{ marginTop: 'var(--space-6)', textAlign: 'center' }}>
          Don't have an account? <Link to="/register" className="text-brand">Sign up</Link>
        </p>
      </Card>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/RegisterPage.jsx': '''
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/store/useAuthStore';

export default function RegisterPage() {
  const login = useAuthStore(state => state.login);
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();
    login({ id: 1, full_name: 'Demo User' }, 'fake-token');
    navigate('/dashboard');
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', padding: 'var(--space-4)' }}>
      <Card style={{ width: '100%', maxWidth: 400, padding: 'var(--space-8)' }}>
        <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-6)', textAlign: 'center' }}>Create an account</h2>
        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <Input label="Full Name" placeholder="Jane Doe" required />
          <Input label="Email address" type="email" placeholder="name@example.com" required />
          <Input label="Password" type="password" required />
          <Button type="submit" size="lg" style={{ marginTop: 'var(--space-2)' }}>Create account</Button>
        </form>
        <p className="text-body-sm text-secondary" style={{ marginTop: 'var(--space-6)', textAlign: 'center' }}>
          Already have an account? <Link to="/login" className="text-brand">Log in</Link>
        </p>
      </Card>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/DashboardPage.jsx': '''
import React from 'react';
import { EmptyState } from '@/components/ui/States';
import { Button } from '@/components/ui/Button';
import { Plus } from 'lucide-react';

export default function DashboardPage() {
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-8)' }}>
        <h1 className="text-heading-lg">Dashboard</h1>
        <Button icon={Plus}>New Course</Button>
      </div>
      <EmptyState 
        title="No courses yet"
        description="Upload a PDF to generate your first interactive learning course."
        action={<Button icon={Plus}>Upload PDF</Button>}
      />
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/CoursesPage.jsx': '''
import React from 'react';
import { Skeleton } from '@/components/ui/Loading';

export default function CoursesPage() {
  return (
    <div>
      <h1 className="text-heading-lg" style={{ marginBottom: 'var(--space-6)' }}>My Courses</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 'var(--space-6)' }}>
        {[1, 2, 3].map(i => (
          <div key={i} style={{ border: '1px solid var(--border-default)', padding: 'var(--space-4)', borderRadius: 'var(--radius-md)' }}>
            <Skeleton height="20px" width="70%" style={{ marginBottom: 'var(--space-2)' }} />
            <Skeleton height="14px" width="40%" style={{ marginBottom: 'var(--space-4)' }} />
            <Skeleton height="8px" width="100%" />
          </div>
        ))}
      </div>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/CourseDetailPage.jsx': '''
import React from 'react';
import { useParams } from 'react-router-dom';
import { Tabs } from '@/components/ui/Tabs';

export default function CourseDetailPage() {
  const { id } = useParams();
  
  return (
    <div>
      <h1 className="text-heading-lg" style={{ marginBottom: 'var(--space-6)' }}>Course Detail ({id})</h1>
      <Tabs 
        tabs={[
          { id: 'lessons', label: 'Lessons' },
          { id: 'quiz', label: 'Quizzes' },
          { id: 'flashcards', label: 'Flashcards' }
        ]} 
      />
      <div style={{ marginTop: 'var(--space-6)' }}>
        <p className="text-secondary">Content will load here...</p>
      </div>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/LessonViewerPage.jsx': '''
import React from 'react';

export default function LessonViewerPage() {
  return (
    <div className="reading-container">
      <h1 className="text-display-xl" style={{ marginBottom: 'var(--space-6)' }}>Lesson Title</h1>
      <div className="text-body-xl" style={{ color: 'var(--text-secondary)' }}>
        <p>This is where the lesson content generated from the PDF will be rendered.</p>
        <p>The reading container restricts the line width to roughly 68 characters for optimal reading experience, as defined in the layout guidelines.</p>
      </div>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/QuizPage.jsx': '''
import React from 'react';
import { Button } from '@/components/ui/Button';

export default function QuizPage() {
  return (
    <div style={{ maxWidth: 600, margin: '0 auto', textAlign: 'center' }}>
      <h2 className="text-heading-md" style={{ marginBottom: 'var(--space-8)' }}>Question 1 of 10</h2>
      <div style={{ marginBottom: 'var(--space-8)', fontSize: '1.25rem' }}>
        What is the primary function of the mitochondria in a cell?
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
        <Button variant="secondary" size="lg">Protein synthesis</Button>
        <Button variant="secondary" size="lg">Energy production</Button>
        <Button variant="secondary" size="lg">Cell division</Button>
        <Button variant="secondary" size="lg">Waste processing</Button>
      </div>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/ChatPage.jsx': '''
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
'''.lstrip(),

    'frontend/src/pages/AnalyticsPage.jsx': '''
import React from 'react';
import { Card } from '@/components/ui/Card';

export default function AnalyticsPage() {
  return (
    <div>
      <h1 className="text-heading-lg" style={{ marginBottom: 'var(--space-6)' }}>Analytics</h1>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-4)' }}>
        <Card>
          <div className="text-label-md text-secondary">Courses Completed</div>
          <div className="text-display-lg">0</div>
        </Card>
        <Card>
          <div className="text-label-md text-secondary">Quizzes Passed</div>
          <div className="text-display-lg">0</div>
        </Card>
        <Card>
          <div className="text-label-md text-secondary">Study Time (hrs)</div>
          <div className="text-display-lg">0</div>
        </Card>
      </div>
    </div>
  );
}
'''.lstrip(),

    'frontend/src/pages/SettingsPage.jsx': '''
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
'''.lstrip()
}

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Page Shells created successfully.")
