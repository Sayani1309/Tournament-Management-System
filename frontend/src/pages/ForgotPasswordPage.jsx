import { useState } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import TextInput from '../components/common/TextInput';
import ErrorBanner from '../components/common/ErrorBanner';
import { forgotPassword } from '../api/authApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [devToken, setDevToken] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await forgotPassword(email);
      setSubmitted(true);
      if (res.data.dev_token) {
        setDevToken(res.data.dev_token);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Forgot Password</h1>

        {submitted ? (
          <div>
            <p className="text-text-primary mb-4">
              If that email exists in our system, a reset link has been sent.
            </p>
            {devToken && (
              <div className="bg-bg-primary rounded-xl p-4 mb-4">
                <p className="text-text-secondary text-xs mb-2">
                  Development mode — reset token (would normally be emailed):
                </p>
                <Link
                  to={`/reset-password?token=${devToken}`}
                  className="text-accent underline break-all text-sm"
                >
                  Click here to reset your password
                </Link>
              </div>
            )}
            <Link to="/auth" className="text-accent underline text-sm">
              Back to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <ErrorBanner message={error} />
            <TextInput
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <Button type="submit" disabled={loading} className="w-full mt-4">
              {loading ? 'Sending...' : 'Send Reset Link'}
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}