import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import Button from '../common/Button';
import TextInput from '../common/TextInput';
import ErrorBanner from '../common/ErrorBanner';
import { useAuth } from '../../hooks/useAuth';
import { getErrorMessage } from '../../utils/errorMessage';

export default function LoginForm({ expectedRole, onSuccessPath }) {
  const navigate = useNavigate();
  const { login, logout } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(email, password);
      if (user.role !== expectedRole) {
        const correctDoor = user.role === 'ORGANIZER' ? 'Organizer' : 'Player';
        await logout();
        setError(`This account is registered as ${correctDoor === 'Organizer' ? 'an' : 'a'} ${correctDoor}. Please use the ${correctDoor} login instead.`);
        return;
      }
      navigate(onSuccessPath);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <ErrorBanner message={error} />
      <TextInput label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <TextInput label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      <Button type="submit" disabled={loading} className="w-full mt-4">
        {loading ? 'Logging in...' : 'Log In'}
      </Button>
      <Link to="/forgot-password" className="text-accent underline text-sm mt-3 inline-block">
        Forgot password?
      </Link>
    </form>
  );
}