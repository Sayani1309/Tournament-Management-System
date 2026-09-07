import { Link } from 'react-router-dom';
import EmptyState from '../common/EmptyState';

export default function ParticipantList({ participants }) {
  if (!participants || participants.length === 0) {
    return <EmptyState message="No participants registered yet." />;
  }
  return (
    <div className="flex flex-col gap-2">
      {participants.map((p) => {
        const info = p.participant;
        const linkPath = info?.player_id
          ? `/players/${info.player_id}/profile`
          : info?.team_id
          ? `/teams/${info.team_id}/roster`
          : null;

        return (
          <div key={p.id} className="bg-card rounded-xl px-4 py-3 text-text-primary flex justify-between">
            {linkPath ? (
              <Link to={linkPath} className="hover:underline">
                {info.name || 'Unknown'}
              </Link>
            ) : (
              <span>{info?.name || 'Unknown'}</span>
            )}
            <span className="text-text-secondary text-sm">{info?.type}</span>
          </div>
        );
      })}
    </div>
  );
}