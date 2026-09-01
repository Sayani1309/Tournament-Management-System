import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../common/Button';
import TextInput from '../common/TextInput';
import ErrorBanner from '../common/ErrorBanner';
import { register } from '../../api/authApi';
import { getErrorMessage } from '../../utils/errorMessage';

export default function OrganizerRegisterForm() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register({ name, email, password, role: 'ORGANIZER' });
      navigate('/organizer/login');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <ErrorBanner message={error} />
      <TextInput label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <TextInput label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <TextInput label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
      <Button type="submit" disabled={loading} className="w-full mt-4">
        {loading ? 'Creating account...' : 'Sign Up'}
      </Button>
    </form>
  );
}