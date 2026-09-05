import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Button from '../components/common/Button';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import { listVenues } from '../api/venueApi';
import { getErrorMessage } from '../utils/errorMessage';
import { useAuth } from '../hooks/useAuth';

export default function VenueListPage() {
  const { role } = useAuth();
  const [venues, setVenues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const res = await listVenues();
        setVenues(res.data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  return (
    <AppShell>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl text-text-primary">Venues</h1>
        {role === 'ORGANIZER' && (
          <Link to="/venues/new">
            <Button>+ Add Venue</Button>
          </Link>
        )}
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <LoadingSpinner />
      ) : venues.length === 0 ? (
        <EmptyState message="No venues added yet." />
      ) : (
        <div className="flex flex-col gap-3">
          {venues.map((v) => (
            <div key={v.id} className="bg-card rounded-2xl p-5">
              <h3 className="text-text-primary text-lg font-semibold">{v.name}</h3>
              <p className="text-text-secondary text-sm">{v.location}</p>
              {v.capacity != null && (
                <p className="text-text-secondary text-xs mt-1">Capacity: {v.capacity}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </AppShell>
  );
}