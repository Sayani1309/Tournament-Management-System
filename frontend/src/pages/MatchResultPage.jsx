import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import ErrorBanner from '../components/common/ErrorBanner';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { getMatch, submitResult } from '../api/matchApi';
import { getTournament } from '../api/tournamentApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function MatchResultPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState('');

  const [scoreA, setScoreA] = useState('');
  const [scoreB, setScoreB] = useState('');
  const [isDraw, setIsDraw] = useState(false);
  const [winnerId, setWinnerId] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const [tournamentFormat, setTournamentFormat] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setLoadError('');
      try {
        const res = await getMatch(id);
        setMatch(res.data);
        const tRes = await getTournament(res.data.tournament_id);
        setTournamentFormat(tRes.data.format);
      } catch (err) {
        setLoadError(getErrorMessage(err));
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

  if (loadError || !match) {
    return (
      <AppShell>
        <Card className="max-w-lg">
          <ErrorBanner message={loadError || 'Match not found.'} />
          <Link to="/organizer/dashboard">
            <Button>Back to Dashboard</Button>
          </Link>
        </Card>
      </AppShell>
    );
  }

  const [participantA, participantB] = match.participants;

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');

    if (!isDraw && !winnerId) {
      setError('Please select a winner, or mark this match as a draw.');
      return;
    }
    if (scoreA === '' || scoreB === '') {
      setError('Please enter both scores.');
      return;
    }

    const payload = {
      result_type: isDraw ? 'DRAW' : 'WIN',
      scores: [
        { participant_id: participantA.id, score: Number(scoreA) },
        { participant_id: participantB.id, score: Number(scoreB) },
      ],
    };
    if (!isDraw) {
      payload.winner_participant_id = Number(winnerId);
    }

    setSubmitting(true);
    try {
      await submitResult(id, payload);
      navigate(`/organizer/tournaments/${match.tournament_id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <AppShell>
      <Card className="max-w-lg">
        <h1 className="text-2xl text-text-primary mb-2">Enter Match Result</h1>
        <p className="text-text-secondary mb-6">{match.round}</p>

        <form onSubmit={handleSubmit}>
          <ErrorBanner message={error} />

          <div className="flex justify-between items-center mb-4 gap-4">
            <div className="flex-1">
              <label className="block text-text-secondary text-sm mb-1">{participantA.name}</label>
              <input
                type="number"
                value={scoreA}
                onChange={(e) => setScoreA(e.target.value)}
                className="w-full bg-transparent border-b border-text-secondary text-text-primary py-2 outline-none focus:border-accent"
                required
              />
            </div>
            <span className="text-text-secondary pt-6">vs</span>
            <div className="flex-1">
              <label className="block text-text-secondary text-sm mb-1">{participantB.name}</label>
              <input
                type="number"
                value={scoreB}
                onChange={(e) => setScoreB(e.target.value)}
                className="w-full bg-transparent border-b border-text-secondary text-text-primary py-2 outline-none focus:border-accent"
                required
              />
            </div>
          </div>

          {tournamentFormat !== 'KNOCKOUT' && (
            <label className="flex items-center gap-2 mb-4 text-text-primary">
              <input
                type="checkbox"
                checked={isDraw}
                onChange={(e) => {
                  setIsDraw(e.target.checked);
                  if (e.target.checked) setWinnerId('');
                }}
              />
              This was a draw
            </label>
          )}

          {!isDraw && (
            <div className="mb-4">
              <label className="block text-text-secondary text-sm mb-2">Winner</label>
              <div className="flex gap-3">
                <Button
                  type="button"
                  variant={winnerId === String(participantA.id) ? 'primary' : 'secondary'}
                  onClick={() => setWinnerId(String(participantA.id))}
                >
                  {participantA.name}
                </Button>
                <Button
                  type="button"
                  variant={winnerId === String(participantB.id) ? 'primary' : 'secondary'}
                  onClick={() => setWinnerId(String(participantB.id))}
                >
                  {participantB.name}
                </Button>
              </div>
            </div>
          )}

          <Button type="submit" disabled={submitting} className="w-full mt-4">
            {submitting ? 'Submitting...' : 'Submit Result'}
          </Button>
        </form>
      </Card>
    </AppShell>
  );
}