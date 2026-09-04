import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import AppShell from '../components/layout/AppShell';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import TextInput from '../components/common/TextInput';
import ErrorBanner from '../components/common/ErrorBanner';
import { createTournament } from '../api/tournamentApi';
import { getErrorMessage } from '../utils/errorMessage';

export default function CreateTournamentPage() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [sport, setSport] = useState('');
  const [format, setFormat] = useState('ROUND_ROBIN');
  const [participantType, setParticipantType] = useState('INDIVIDUAL');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await createTournament({
        name,
        description: description || undefined,
        sport,
        format,
        participant_type: participantType,
      });
      navigate(`/organizer/tournaments/${res.data.id}`);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppShell>
      <Card className="max-w-xl">
        <h1 className="text-2xl text-text-primary mb-6">Create a Tournament</h1>
        <form onSubmit={handleSubmit}>
          <ErrorBanner message={error} />
          <TextInput label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
          <TextInput label="Sport" value={sport} onChange={(e) => setSport(e.target.value)} required />
          <TextInput
            label="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />

          <div className="mb-4">
            <label className="block text-text-secondary text-sm mb-2">Format</label>
            <div className="flex gap-3">
              <Button type="button" variant={format === 'ROUND_ROBIN' ? 'primary' : 'secondary'} onClick={() => setFormat('ROUND_ROBIN')}>
                Round Robin
              </Button>
              <Button type="button" variant={format === 'KNOCKOUT' ? 'primary' : 'secondary'} onClick={() => setFormat('KNOCKOUT')}>
                Knockout
              </Button>
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-text-secondary text-sm mb-2">Participant Type</label>
            <div className="flex gap-3">
              <Button type="button" variant={participantType === 'INDIVIDUAL' ? 'primary' : 'secondary'} onClick={() => setParticipantType('INDIVIDUAL')}>
                Individual
              </Button>
              <Button type="button" variant={participantType === 'TEAM' ? 'primary' : 'secondary'} onClick={() => setParticipantType('TEAM')}>
                Team
              </Button>
            </div>
          </div>

          <Button type="submit" disabled={loading} className="w-full mt-4">
            {loading ? 'Creating...' : 'Create Tournament'}
          </Button>
        </form>
      </Card>
    </AppShell>
  );
}