import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Button from '../components/common/Button';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import EmptyState from '../components/common/EmptyState';
import { listTournaments } from '../api/tournamentApi';
import { getErrorMessage } from '../utils/errorMessage';
import { useAuth } from '../hooks/useAuth';

export default function OrganizerDashboardPage() {
  const { user } = useAuth();
  const [tournaments, setTournaments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        // No backend filter for "mine" — fetch a generous page and filter client-side.
        const res = await listTournaments({ perPage: 100 });
        const mine = res.data.items.filter((t) => t.organizer_id === user?.id);
        setTournaments(mine);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }
    if (user) load();
  }, [user]);

  return (
    <AppShell>
      <div className="bg-gradient-to-r from-bg-secondary to-accent rounded-3xl p-8 mb-8 flex justify-between items-center flex-wrap gap-4">
        <div>
          <h1 className="text-3xl text-text-primary">Hello, {user?.name}</h1>
          <p className="text-text-secondary mt-2">Manage your tournaments.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/venues">
            <Button variant="secondary">Manage Venues</Button>
          </Link>
          <Link to="/organizer/tournaments/new">
            <Button>+ Create Tournament</Button>
          </Link>
        </div>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <LoadingSpinner />
      ) : tournaments.length === 0 ? (
        <EmptyState message="You haven't created any tournaments yet." />
      ) : (
        <div className="flex flex-col gap-3">
          {tournaments.map((t) => (
            <Link
              key={t.id}
              to={`/organizer/tournaments/${t.id}`}
              className="bg-card rounded-2xl p-5 flex justify-between items-center hover:opacity-90"
            >
              <div>
                <h3 className="text-text-primary text-lg font-semibold">{t.name}</h3>
                <p className="text-text-secondary text-sm">
                  {t.sport} · {t.format.replace('_', ' ')} · {t.participant_type}
                </p>
              </div>
              <StatusBadge status={t.status} />
            </Link>
          ))}
        </div>
      )}
    </AppShell>
  );
}