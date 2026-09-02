import { Link } from 'react-router-dom';
import EmptyState from '../common/EmptyState';
import StatusBadge from '../common/StatusBadge';

export default function MatchList({ matches }) {
  if (!matches || matches.length === 0) {
    return <EmptyState message="Fixtures haven't been generated yet." />;
  }
  return (
    <div className="flex flex-col gap-2">
      {matches.map((m) => (
        <Link
          key={m.id}
          to={`/matches/${m.id}`}
          className="bg-card rounded-xl px-4 py-3 flex justify-between items-center hover:opacity-90"
        >
          <div>
            <div className="text-text-secondary text-xs mb-1">{m.round}</div>
            <div className="text-text-primary">
              {m.participants.map((p) => p.name).join(' vs ')}
            </div>
          </div>
          <StatusBadge status={m.status} />
        </Link>
      ))}
    </div>
  );
}