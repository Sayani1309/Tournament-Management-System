import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import Button from '../components/common/Button';
import ParticipantList from '../components/tournament/ParticipantList';
import MatchList from '../components/tournament/MatchList';
import StandingsTable from '../components/tournament/StandingsTable';
import ChampionBanner from '../components/tournament/ChampionBanner';
import { getTournament } from '../api/tournamentApi';
import { listParticipants, registerParticipant } from '../api/participantApi';
import { listMatches } from '../api/matchApi';
import { getStandings } from '../api/standingsApi';
import { getErrorMessage } from '../utils/errorMessage';
import { useAuth } from '../hooks/useAuth';
import { listVenues } from '../api/venueApi';

const TABS = ['Participants', 'Fixtures', 'Standings'];

export default function TournamentDetailPage() {
  const { id } = useParams();
  const { isAuthenticated, role, user } = useAuth();
  const [tournament, setTournament] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [activeTab, setActiveTab] = useState('Participants');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [joinError, setJoinError] = useState('');
  const [joining, setJoining] = useState(false);
  const [joined, setJoined] = useState(false);
  const [venues, setVenues] = useState([]);
  async function loadAll() {
    setLoading(true);
    setError('');
    try {
      const [tRes, pRes, mRes, sRes, vRes] = await Promise.all([
        getTournament(id),
        listParticipants(id),
        listMatches(id),
        getStandings(id),
        listVenues(),
      ]);
      setTournament(tRes.data);
      setParticipants(pRes.data);
      setMatches(mRes.data);
      setStandings(sRes.data);
      setVenues(vRes.data);

      if (role === 'PLAYER' && user?.player_id) {
        const alreadyIn = pRes.data.some((p) => p.participant?.player_id === user.player_id);
        setJoined(alreadyIn);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAll();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleJoin() {
    setJoinError('');
    setJoining(true);
    try {
      await registerParticipant(id, { player_id: user.player_id });
      await loadAll();
    } catch (err) {
      setJoinError(getErrorMessage(err));
    } finally {
      setJoining(false);
    }
  }

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

  const canShowJoin =
    isAuthenticated &&
    role === 'PLAYER' &&
    tournament.status === 'REGISTRATION_OPEN' &&
    tournament.participant_type === 'INDIVIDUAL' &&
    !joined;

  const isTeamTournamentForPlayer =
    isAuthenticated &&
    role === 'PLAYER' &&
    tournament.status === 'REGISTRATION_OPEN' &&
    tournament.participant_type === 'TEAM';

  return (
    <AppShell>
      <div className="mb-6">
        <div className="flex items-center gap-4 mb-2 flex-wrap">
          <h1 className="text-3xl text-text-primary">{tournament.name}</h1>
          <StatusBadge status={tournament.status} />
        </div>
        <p className="text-text-secondary">
          {tournament.sport} · {tournament.format.replace('_', ' ')} · {tournament.participant_type}
        </p>
        {tournament.description && (
          <p className="text-text-primary mt-3">{tournament.description}</p>
        )}

        {canShowJoin && (
          <div className="mt-4">
            <ErrorBanner message={joinError} />
            <Button onClick={handleJoin} disabled={joining}>
              {joining ? 'Joining...' : 'Join this tournament'}
            </Button>
          </div>
        )}

        {joined && (
          <p className="text-text-secondary mt-4">You're registered for this tournament.</p>
        )}

        {isTeamTournamentForPlayer && (
          <p className="text-text-secondary mt-4">
            This is a team tournament — contact the organizer to register your team:{' '}
            <a href={`mailto:${tournament.organizer_email}`} className="text-accent underline">
              {tournament.organizer_name} ({tournament.organizer_email})
            </a>
          </p>
        )}
      </div>
      <ChampionBanner tournament={tournament} matches={matches} standings={standings} />
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
      {activeTab === 'Fixtures' && <MatchList matches={matches} venues={venues} />}
      {activeTab === 'Standings' && <StandingsTable standings={standings} />}
    </AppShell>
  );
}