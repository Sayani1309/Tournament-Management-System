import ConfirmDialog from '../components/common/ConfirmDialog';
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import ChampionBanner from '../components/tournament/ChampionBanner';
import StandingsTable from '../components/tournament/StandingsTable';
import {
  getTournament,
  openRegistration,
  startTournament,
} from '../api/tournamentApi';
import { listParticipants, registerParticipant, removeParticipant } from '../api/participantApi';
import { listMatches, generateFixtures, scheduleMatch } from '../api/matchApi';
import { getStandings } from '../api/standingsApi';
import { listPlayers } from '../api/playerApi';
import { listTeams } from '../api/teamApi';
import { listVenues } from '../api/venueApi';
import { getErrorMessage } from '../utils/errorMessage';
import LoadingOverlay from '../components/common/LoadingOverlay';
import Toast from '../components/common/Toast';

function matchLabel(participants) {
  if (participants.length === 2) return `${participants[0].name} vs ${participants[1].name}`;
  if (participants.length === 1) return `${participants[0].name} vs TBA`;
  return 'TBA vs TBA';
}

function ParticipantLink({ p }) {
  const path = p.player_id
    ? `/players/${p.player_id}/profile`
    : p.team_id
    ? `/teams/${p.team_id}/roster`
    : null;
  if (!path) return <span>{p.name}</span>;
  return (
    <Link to={path} onClick={(e) => e.stopPropagation()} className="hover:underline">
      {p.name}
    </Link>
  );
}

function MatchParticipants({ participants }) {
  if (participants.length === 2) {
    return (
      <>
        <ParticipantLink p={participants[0]} /> vs <ParticipantLink p={participants[1]} />
      </>
    );
  }
  if (participants.length === 1) {
    return (
      <>
        <ParticipantLink p={participants[0]} /> vs TBA
      </>
    );
  }
  return <>TBA vs TBA</>;
}

function MatchScheduleRow({ match, venues, onScheduled }) {
  const [venueId, setVenueId] = useState(match.venue_id || '');
  const [scheduledAt, setScheduledAt] = useState(
    match.scheduled_at ? match.scheduled_at.slice(0, 16) : ''
  );
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [savedFlash, setSavedFlash] = useState(false);

  async function handleSave() {
    setError('');
    setSaving(true);
    try {
      const payload = {};
      if (venueId) payload.venue_id = Number(venueId);
      if (scheduledAt) payload.scheduled_at = new Date(scheduledAt).toISOString();
      await scheduleMatch(match.id, payload);
      setSavedFlash(true);
      setTimeout(() => setSavedFlash(false), 2000);
      onScheduled();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="bg-bg-primary rounded-xl px-4 py-3">
      <div className="flex justify-between items-center mb-2">
        <div>
          <div className="text-text-secondary text-xs mb-1">{match.round}</div>
          <div className="text-text-primary">
            {match.participants.length === 2 ? (
              <>
                <Link to={match.participants[0].player_id ? `/players/${match.participants[0].player_id}/profile` : `/teams/${match.participants[0].team_id}/roster`} onClick={(e) => e.stopPropagation()} className="hover:underline">
                  {match.participants[0].name}
                </Link>
                {' vs '}
                <Link to={match.participants[1].player_id ? `/players/${match.participants[1].player_id}/profile` : `/teams/${match.participants[1].team_id}/roster`} onClick={(e) => e.stopPropagation()} className="hover:underline">
                  {match.participants[1].name}
                </Link>
              </>
            ) : (
              matchLabel(match.participants)
            )}
          </div>
        </div>
        {match.status === 'SCHEDULED' && match.participants.length === 2 ? (
          match.venue_id && match.scheduled_at ? (
            <Link to={`/organizer/matches/${match.id}/result`}>
              <Button>Enter Result</Button>
            </Link>
          ) : (
            <Button disabled title="Set a venue and schedule first">
              Enter Result
            </Button>
          )
        ) : (
          <StatusBadge status={match.status} />
        )}
      </div>

      {match.status === 'SCHEDULED' && (
        <div className="flex gap-3 items-end flex-wrap mt-3">
          <ErrorBanner message={error} />
          <div>
            <label className="block text-text-secondary text-xs mb-1">Venue</label>
            <select
              className="bg-transparent border-b border-text-secondary text-text-primary py-1 outline-none focus:border-accent"
              value={venueId}
              onChange={(e) => setVenueId(e.target.value)}
            >
              <option value="" className="bg-card">No venue</option>
              {venues.map((v) => (
                <option key={v.id} value={v.id} className="bg-card">{v.name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-text-secondary text-xs mb-1">Date & Time</label>
            <input
              type="datetime-local"
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              className="bg-transparent border-b border-text-secondary text-text-primary py-1 outline-none focus:border-accent"
            />
          </div>
          <Button variant="secondary" onClick={handleSave} disabled={saving}>
            {saving ? 'Saving...' : 'Save Schedule'}
          </Button>
          {savedFlash && <span className="text-text-primary text-sm">✓ Saved</span>}
        </div>
      )}
    </div>
  );
}

export default function TournamentManagementPage() {
  const { id } = useParams();
  const [tournament, setTournament] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [matches, setMatches] = useState([]);
  const [standings, setStandings] = useState([]);
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [venues, setVenues] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionError, setActionError] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [confirmRemove, setConfirmRemove] = useState(null); // holds the participant being confirmed, or null

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
      <LoadingOverlay show={actionLoading} />
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
                  onClick={() => setConfirmRemove(p)}
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
              <div className="flex flex-col gap-3">
                {matches.map((m) => (
                  <MatchScheduleRow key={m.id} match={m} venues={venues} onScheduled={loadAll} />
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
      <ConfirmDialog
        open={!!confirmRemove}
        title="Remove participant?"
        message={`Are you sure you want to remove "${confirmRemove?.participant?.name}" from this tournament?`}
        confirmLabel="Remove"
        loading={actionLoading}
        onCancel={() => setConfirmRemove(null)}
        onConfirm={async () => {
          await runAction(() => removeParticipant(id, confirmRemove.participant_id));
          setConfirmRemove(null);
        }}
      />
    </AppShell>
  );
}