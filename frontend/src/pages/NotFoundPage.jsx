import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="app-gradient-bg flex items-center justify-center p-8">
      <div className="bg-card rounded-3xl p-8 max-w-md text-center">
        <h1 className="text-3xl text-text-primary mb-3">404</h1>
        <p className="text-text-secondary mb-6">
          This page doesn't exist, or you don't have access to it.
        </p>
        <Link
          to="/"
          className="inline-block px-6 py-2 rounded-full bg-accent text-text-primary font-medium hover:opacity-90"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
}