import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../common/Button';
import TextInput from '../common/TextInput';
import ErrorBanner from '../common/ErrorBanner';
import { register } from '../../api/authApi';
import { listTeams } from '../../api/teamApi';
import { getErrorMessage } from '../../utils/errorMessage';

export default function PlayerRegisterForm() {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [participationType, setParticipationType] = useState('INDIVIDUAL');
  const [teamOption, setTeamOption] = useState('NEW');
  const [teamName, setTeamName] = useState('');
  const [teamId, setTeamId] = useState('');
  const [teams, setTeams] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (participationType === 'TEAM' && teamOption === 'EXISTING') {
      listTeams().then((res) => setTeams(res.data.items)).catch(() => setTeams([]));
    }
  }, [participationType, teamOption]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    const payload = {
      name,
      email,
      password,
      role: 'PLAYER',
      participation_type: participationType,
    };

    if (participationType === 'TEAM') {
      payload.team_option = teamOption;
      if (teamOption === 'NEW') {
        payload.team_name = teamName;
      } else {
        payload.team_id = Number(teamId);
      }
    }

    try {
      await register(payload);
      navigate('/player/login');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <ErrorBanner message={error} />
      <TextInput label="Name" value={name} onChange={(e) => setName(e.target.value)} required />
      <TextInput label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      <TextInput label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />

      <div className="mb-4">
        <label className="block text-text-secondary text-sm mb-2">Participation Type</label>
        <div className="flex gap-3">
          <Button
            type="button"
            variant={participationType === 'INDIVIDUAL' ? 'primary' : 'secondary'}
            onClick={() => setParticipationType('INDIVIDUAL')}
          >
            Individual
          </Button>
          <Button
            type="button"
            variant={participationType === 'TEAM' ? 'primary' : 'secondary'}
            onClick={() => setParticipationType('TEAM')}
          >
            Team
          </Button>
        </div>
      </div>

      {participationType === 'TEAM' && (
        <>
          <div className="mb-4">
            <label className="block text-text-secondary text-sm mb-2">Team Option</label>
            <div className="flex gap-3">
              <Button
                type="button"
                variant={teamOption === 'NEW' ? 'primary' : 'secondary'}
                onClick={() => setTeamOption('NEW')}
              >
                New Team
              </Button>
              <Button
                type="button"
                variant={teamOption === 'EXISTING' ? 'primary' : 'secondary'}
                onClick={() => setTeamOption('EXISTING')}
              >
                Existing Team
              </Button>
            </div>
          </div>

          {teamOption === 'NEW' ? (
            <TextInput
              label="Team Name"
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              required
            />
          ) : (
            <div className="mb-4">
              <label className="block text-text-secondary text-sm mb-1">Select Team</label>
              <select
                className="w-full bg-transparent border-b border-text-secondary text-text-primary py-2 outline-none focus:border-accent"
                value={teamId}
                onChange={(e) => setTeamId(e.target.value)}
                required
              >
                <option value="" className="bg-card">Choose a team...</option>
                {teams.map((t) => (
                  <option key={t.id} value={t.id} className="bg-card">{t.name}</option>
                ))}
              </select>
            </div>
          )}
        </>
      )}

      <Button type="submit" disabled={loading} className="w-full mt-4">
        {loading ? 'Creating account...' : 'Sign Up'}
      </Button>
    </form>
  );
}