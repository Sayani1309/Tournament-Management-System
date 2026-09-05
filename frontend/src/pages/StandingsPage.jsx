import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import StandingsTable from '../components/tournament/StandingsTable';
import ChampionBanner from '../components/tournament/ChampionBanner';
import { getTournament } from '../api/tournamentApi';
import { listMatches } from '../api/matchApi';
import { getStandings } from '../api/standingsApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function StandingsPage() {
  const { id } = useParams();
  const [tournament, setTournament] = useState(null);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [tRes, mRes, sRes] = await Promise.all([
          getTournament(id),
          listMatches(id),
          getStandings(id),
        ]);
        setTournament(tRes.data);
        setMatches(mRes.data);
        setStandings(sRes.data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <AppShell>
        <LoadingSpinner />
      </AppShell>
    );
  }

  if (error || !tournament) {
    return (
      <AppShell>
        <ErrorBanner message={error || 'Tournament not found.'} />
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="mb-6">
        <h1 className="text-3xl text-text-primary">{tournament.name} — Standings</h1>
        <Link to={`/tournaments/${id}`} className="text-accent underline text-sm">
          Back to tournament
        </Link>
      </div>

      <ChampionBanner tournament={tournament} matches={matches} standings={standings} />

      <Card>
        <StandingsTable standings={standings} />
      </Card>
    </AppShell>
  );
}