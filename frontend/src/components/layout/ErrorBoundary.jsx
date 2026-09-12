import { Component } from 'react';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error('Unhandled UI error:', error, info);
  }

  handleReload = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="app-gradient-bg flex items-center justify-center p-8">
          <div className="bg-card rounded-3xl p-8 max-w-md text-center">
            <h1 className="text-2xl text-text-primary mb-3">Something went wrong</h1>
            <p className="text-text-secondary mb-6">
              An unexpected error occurred. Try reloading the page.
            </p>
            <button
              onClick={this.handleReload}
              className="px-6 py-2 rounded-full bg-accent text-text-primary font-medium hover:opacity-90"
            >
              Back to Home
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}