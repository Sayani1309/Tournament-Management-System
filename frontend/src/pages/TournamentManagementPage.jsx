import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import ParticipantList from '../components/tournament/ParticipantList';
import MatchList from '../components/tournament/MatchList';
import StandingsTable from '../components/tournament/StandingsTable';
import ChampionBanner from '../components/tournament/ChampionBanner';
import {
  getTournament,
  openRegistration,
  startTournament,
} from '../api/tournamentApi';
import { listParticipants, registerParticipant, removeParticipant } from '../api/participantApi';
import { listMatches, generateFixtures } from '../api/matchApi';
import { getStandings } from '../api/standingsApi';
import { listPlayers } from '../api/playerApi';
import { listTeams } from '../api/teamApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function TournamentManagementPage() {
  const { id } = useParams();
  const [tournament, setTournament] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionError, setActionError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);

  async function loadAll() {
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

      if (tRes.data.status === 'REGISTRATION_OPEN') {
        if (tRes.data.participant_type === 'INDIVIDUAL') {
          const plRes = await listPlayers();
          setPlayers(plRes.data.items);
        } else {
          const tmRes = await listTeams();
          setTeams(tmRes.data.items);
        }
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

  async function runAction(fn) {
    setActionError('');
    setActionLoading(true);
    try {
      await fn();
      await loadAll();
    } catch (err) {
      setActionError(getErrorMessage(err));
    } finally {
      setActionLoading(false);
    }
  }

  async function handleAddParticipant() {
    if (!selectedId) return;
    const payload =
      tournament.participant_type === 'INDIVIDUAL'
        ? { player_id: Number(selectedId) }
        : { team_id: Number(selectedId) };
    await runAction(() => registerParticipant(id, payload));
    setSelectedId('');
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

  const options = tournament.participant_type === 'INDIVIDUAL' ? players : teams;

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
      </div>
      <ChampionBanner tournament={tournament} matches={matches} standings={standings} />
      <ErrorBanner message={actionError} />

      {tournament.status === 'DRAFT' && (
        <Card className="mb-6">
          <p className="text-text-primary mb-4">
            This tournament is in draft. Open registration to let participants join.
          </p>
          <Button onClick={() => runAction(() => openRegistration(id))} disabled={actionLoading}>
            {actionLoading ? 'Opening...' : 'Open Registration'}
          </Button>
        </Card>
      )}

      {tournament.status === 'REGISTRATION_OPEN' && (
        <Card className="mb-6">
          <h2 className="text-xl text-text-primary mb-4">Register a Participant</h2>
          <div className="flex gap-3 items-end flex-wrap mb-4">
            <div className="flex-1 min-w-[200px]">
              <select
                className="w-full bg-transparent border-b border-text-secondary text-text-primary py-2 outline-none focus:border-accent"
                value={selectedId}
                onChange={(e) => setSelectedId(e.target.value)}
              >
                <option value="" className="bg-card">
                  Choose a {tournament.participant_type === 'INDIVIDUAL' ? 'player' : 'team'}...
                </option>
                {options.map((o) => (
                  <option key={o.id} value={o.id} className="bg-card">{o.name}</option>
                ))}
              </select>
            </div>
            <Button onClick={handleAddParticipant} disabled={actionLoading || !selectedId}>
              Add
            </Button>
          </div>

          <h3 className="text-text-secondary text-sm mb-2">
            Registered ({participants.length})
          </h3>
          <div className="flex flex-col gap-2 mb-4">
            {participants.map((p) => (
              <div key={p.id} className="bg-bg-primary rounded-xl px-4 py-2 flex justify-between items-center">
                <span className="text-text-primary">{p.participant?.name}</span>
                <button
                  onClick={() => runAction(() => removeParticipant(id, p.participant_id))}
                  className="text-accent text-sm hover:underline"
                  disabled={actionLoading}
                >
                  Remove
                </button>
              </div>
            ))}
          </div>

          <Button onClick={() => runAction(() => startTournament(id))} disabled={actionLoading}>
            {actionLoading ? 'Starting...' : 'Start Tournament'}
          </Button>
        </Card>
      )}

      {tournament.status === 'ONGOING' && (
        <Card className="mb-6">
          {matches.length === 0 ? (
            <>
              <p className="text-text-primary mb-4">
                Fixtures haven't been generated yet.
              </p>
              <Button onClick={() => runAction(() => generateFixtures(id))} disabled={actionLoading}>
                {actionLoading ? 'Generating...' : 'Generate Fixtures'}
              </Button>
            </>
          ) : (
            <>
              <h2 className="text-xl text-text-primary mb-4">Matches</h2>
              <div className="flex flex-col gap-2">
                {matches.map((m) => (
                  <div key={m.id} className="bg-bg-primary rounded-xl px-4 py-3 flex justify-between items-center">
                    <div>
                      <div className="text-text-secondary text-xs mb-1">{m.round}</div>
                      <div className="text-text-primary">{m.participants.map((p) => p.name).join(' vs ')}</div>
                    </div>
                    {m.status === 'SCHEDULED' ? (
                      <Link to={`/organizer/matches/${m.id}/result`}>
                        <Button>Enter Result</Button>
                      </Link>
                    ) : (
                      <StatusBadge status={m.status} />
                    )}
                  </div>
                ))}
              </div>
            </>
          )}
        </Card>
      )}

      {tournament.status === 'COMPLETED' && (
        <Card className="mb-6">
          <h2 className="text-xl text-text-primary mb-4">Final Standings</h2>
          <StandingsTable standings={standings} />
        </Card>
      )}

      {tournament.status !== 'COMPLETED' && (
        <Card>
          <h2 className="text-xl text-text-primary mb-4">Current Standings</h2>
          <StandingsTable standings={standings} />
        </Card>
      )}
    </AppShell>
  );
}