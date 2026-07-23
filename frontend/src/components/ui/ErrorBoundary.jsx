import React from 'react';
import { Button } from './Button';
import { EmptyState } from './States';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
    // Reload page to reset state completely if simple retry fails
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <EmptyState
            icon="AlertTriangle"
            title="Something went wrong"
            description="We encountered an unexpected error. Please try again or refresh the page."
            action={
              <Button onClick={this.handleRetry} variant="primary">
                Refresh Page
              </Button>
            }
          />
        </div>
      );
    }

    return this.props.children;
  }
}
