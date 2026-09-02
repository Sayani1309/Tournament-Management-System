import { useEffect, useState } from 'react';
import AppShell from '../components/layout/AppShell';
import TournamentList from '../components/tournament/TournamentList';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import { listTournaments } from '../api/tournamentApi';
import { getErrorMessage } from '../utils/errorMessage';
import { useAuth } from '../hooks/useAuth';

export default function HomePage() {
  const { user } = useAuth();
  const [upcoming, setUpcoming] = useState([]);
  const [live, setLive] = useState([]);
  const [completed, setCompleted] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [regOpen, ongoing, done] = await Promise.all([
          listTournaments({ status: 'REGISTRATION_OPEN', perPage: 10 }),
          listTournaments({ status: 'ONGOING', perPage: 10 }),
          listTournaments({ status: 'COMPLETED', perPage: 5 }),
        ]);
        setUpcoming(regOpen.data.items);
        setLive(ongoing.data.items);
        setCompleted(done.data.items);
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
        <h1 className="text-3xl text-text-primary">
          Hello{user ? `, ${user.name}` : ''}
        </h1>
        <p className="text-text-secondary mt-2">
          Browse tournaments, view live matches, and check results.
        </p>
      </div>

      <ErrorBanner message={error} />
      {loading ? (
        <LoadingSpinner />
      ) : (
        <>
          {live.length > 0 && (
            <section className="mb-8">
              <h2 className="text-2xl text-text-primary mb-4">🔴 Live</h2>
              <TournamentList tournaments={live} />
            </section>
          )}

          <section className="mb-8">
            <h2 className="text-2xl text-text-primary mb-4">Upcoming Tournaments</h2>
            <TournamentList tournaments={upcoming} />
          </section>

          {completed.length > 0 && (
            <section className="mb-8">
              <h2 className="text-2xl text-text-primary mb-4">Previous Results</h2>
              <TournamentList tournaments={completed} />
            </section>
          )}
        </>
      )}
    </AppShell>
  );
}