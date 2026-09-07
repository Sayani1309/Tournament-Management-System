import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ErrorBanner from '../components/common/ErrorBanner';
import StatusBadge from '../components/common/StatusBadge';
import { getMatch, getResult } from '../api/matchApi';
import { getErrorMessage } from '../utils/errorMessage';
import { listVenues } from '../api/venueApi';

export default function MatchScoreCardPage() {
  const { id } = useParams();
  const [match, setMatch] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [venues, setVenues] = useState([]);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError('');
      try {
        const [mRes, vRes] = await Promise.all([getMatch(id), listVenues()]);
        setMatch(mRes.data);
        setVenues(vRes.data);
        if (mRes.data.status === 'COMPLETED') {
          const rRes = await getResult(id);
          setResult(rRes.data);
        }
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

  if (error || !match) {
    return (
      <AppShell>
        <ErrorBanner message={error || 'Match not found.'} />
      </AppShell>
    );
  }

  const scoreFor = (participantId) =>
    result?.scores.find((s) => s.participant.id === participantId)?.score ?? '—';

  return (
    <AppShell>
      <Card className="max-w-2xl">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-2xl text-text-primary">Match Result</h1>
            <p className="text-text-secondary text-sm mt-1">{match.round}</p>
            {(match.venue_id || match.scheduled_at) && (
              <p className="text-text-secondary text-xs mt-1">
                {venues.find((v) => v.id === match.venue_id)?.name && (
                  <>📍 {venues.find((v) => v.id === match.venue_id).name}</>
                )}
                {match.venue_id && match.scheduled_at && ' · '}
                {match.scheduled_at && (
                  <>🕒 {new Date(match.scheduled_at).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}</>
                )}
              </p>
            )}
          </div>
          <StatusBadge status={match.status} />
        </div>

        <div className="flex flex-col gap-4">
          {match.participants.map((p) => {
            const isWinner = result?.winner?.id === p.id;
            const linkPath = p.player_id
              ? `/players/${p.player_id}/profile`
              : p.team_id
              ? `/teams/${p.team_id}/roster`
              : null;
            return (
              <div
                key={p.id}
                className={`rounded-2xl p-5 flex justify-between items-center ${
                  isWinner ? 'bg-accent' : 'bg-bg-primary'
                }`}
              >
                <div>
                  {linkPath ? (
                    <Link to={linkPath} className="text-text-primary text-lg font-semibold hover:underline">
                      {p.name}
                    </Link>
                  ) : (
                    <p className="text-text-primary text-lg font-semibold">{p.name}</p>
                  )}
                  <p className="text-text-secondary text-xs">{p.type}</p>
                </div>
                <div className="text-text-primary text-3xl font-bold">
                  {scoreFor(p.id)}
                </div>
              </div>
            );
          })}
        </div>

        {result && (
          <div className="mt-6 text-center">
            {result.result_type === 'DRAW' ? (
              <p className="text-text-secondary text-lg">Match ended in a draw</p>
            ) : (
              <p className="text-text-primary text-lg">
                🏆 Winner: <span className="font-semibold">{result.winner?.name}</span>
              </p>
            )}
            <p className="text-text-secondary text-xs mt-2">
              Submitted {new Date(result.submitted_at).toLocaleString()}
            </p>
          </div>
        )}

        {!result && match.status === 'SCHEDULED' && (
          <p className="text-text-secondary text-center mt-6">
            This match hasn't been played yet.
          </p>
        )}

        <Link to={`/tournaments/${match.tournament_id}`} className="block text-center text-accent mt-6 underline">
          Back to tournament
        </Link>
      </Card>
    </AppShell>
  );
}