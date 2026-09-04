import { useEffect, useState } from 'react';
import AppShell from '../components/layout/AppShell';
import TournamentList from '../components/tournament/TournamentList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import { getMyTournaments } from '../api/authApi';
import { getErrorMessage } from '../utils/errorMessage';
import { useAuth } from '../hooks/useAuth';

export default function PlayerDashboardPage() {
  const { user } = useAuth();
  const [upcoming, setUpcoming] = useState([]);
  const [past, setPast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const res = await getMyTournaments();
        setUpcoming(res.data.upcoming);
        setPast(res.data.past);
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
      <div className="bg-gradient-to-r from-bg-secondary to-accent rounded-3xl p-8 mb-8">
        <h1 className="text-3xl text-text-primary">Hello, {user?.name}</h1>
        <p className="text-text-secondary mt-2">
          Your tournaments, upcoming and past.
          {user?.team_name && ` · Team: ${user.team_name}`}
        </p>
      </div>

      <ErrorBanner message={error} />

      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          <section className="mb-8">
            <h2 className="text-2xl text-text-primary mb-4">Upcoming Tournaments</h2>
            <TournamentList tournaments={upcoming} />
          </section>

          <section className="mb-8">
            <h2 className="text-2xl text-text-primary mb-4">Previous Tournaments</h2>
            <TournamentList tournaments={past} />
          </section>
        </>
      )}
    </AppShell>
  );
}