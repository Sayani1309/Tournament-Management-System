import { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import TextInput from '../components/common/TextInput';
import ErrorBanner from '../components/common/ErrorBanner';
import { resetPassword } from '../api/authApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function ResetPasswordPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const tokenFromUrl = searchParams.get('token') || '';

  const [token, setToken] = useState(tokenFromUrl);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      await resetPassword(token, newPassword);
      setSuccess(true);
      setTimeout(() => navigate('/auth'), 2500);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Reset Password</h1>

        {success ? (
          <p className="text-text-primary">
            Password reset successfully. Redirecting to login...
          </p>
        ) : (
          <form onSubmit={handleSubmit}>
            <ErrorBanner message={error} />
            <TextInput
              label="Reset Token"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              required
            />
            <TextInput
              label="New Password"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={8}
            />
            <TextInput
              label="Confirm New Password"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              minLength={8}
            />
            <Button type="submit" disabled={loading} className="w-full mt-4">
              {loading ? 'Resetting...' : 'Reset Password'}
            </Button>
          </form>
        )}

        <Link to="/auth" className="text-accent underline text-sm mt-4 inline-block">
          Back to login
        </Link>
      </Card>
    </div>
  );
}