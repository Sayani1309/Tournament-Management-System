import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import TextInput from '../components/common/TextInput';
import ErrorBanner from '../components/common/ErrorBanner';
import { createVenue } from '../api/venueApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function CreateVenuePage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [location, setLocation] = useState('');
  const [capacity, setCapacity] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await createVenue({
        name,
        location,
        capacity: capacity ? Number(capacity) : undefined,
      });
      navigate('/venues');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <Card className="max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Add Venue</h1>
        <form onSubmit={handleSubmit}>
          <ErrorBanner message={error} />
          <TextInput label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
          <TextInput label="Location" value={location} onChange={(e) => setLocation(e.target.value)} required />
          <TextInput
            label="Capacity (optional)"
            type="number"
            value={capacity}
            onChange={(e) => setCapacity(e.target.value)}
          />
          <Button type="submit" disabled={loading} className="w-full mt-4">
            {loading ? 'Adding...' : 'Add Venue'}
          </Button>
        </form>
      </Card>
    </AppShell>
  );
}