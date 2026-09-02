import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import ParticipantList from '../components/tournament/ParticipantList';
import MatchList from '../components/tournament/MatchList';
import StandingsTable from '../components/tournament/StandingsTable';
import { getTournament } from '../api/tournamentApi';
import { listParticipants } from '../api/participantApi';
import { listMatches } from '../api/matchApi';
import { getStandings } from '../api/standingsApi';
import { getErrorMessage } from '../utils/errorMessage';

const TABS = ['Participants', 'Fixtures', 'Standings'];

export default function TournamentDetailPage() {
  const { id } = useParams();
  const [tournament, setTournament] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [activeTab, setActiveTab] = useState('Participants');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [tRes, pRes, mRes, sRes] = await Promise.all([
          getTournament(id),
          listParticipants(id),
          listMatches(id),
          getStandings(id),
        ]);
        setTournament(tRes.data);
        setParticipants(pRes.data);
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
        <div className="flex items-center gap-4 mb-2">
          <h1 className="text-3xl text-text-primary">{tournament.name}</h1>
          <StatusBadge status={tournament.status} />
        </div>
        <p className="text-text-secondary">
          {tournament.sport} · {tournament.format.replace('_', ' ')} · {tournament.participant_type}
        </p>
        {tournament.description && (
          <p className="text-text-primary mt-3">{tournament.description}</p>
        )}
      </div>

      <div className="flex gap-2 mb-6">
        {TABS.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-full ${
              activeTab === tab ? 'bg-accent text-text-primary' : 'bg-card text-text-secondary'
            }`}
          >
            {tab}
          </button>
        ))}
      </div>

      {activeTab === 'Participants' && <ParticipantList participants={participants} />}
      {activeTab === 'Fixtures' && <MatchList matches={matches} />}
      {activeTab === 'Standings' && <StandingsTable standings={standings} />}
    </AppShell>
  );
}