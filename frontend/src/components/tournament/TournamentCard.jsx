import { Link } from 'react-router-dom';
import StatusBadge from '../common/StatusBadge';

const COLORS = ['bg-emerald-900', 'bg-blue-900', 'bg-purple-900', 'bg-rose-900'];

export default function TournamentCard({ tournament }) {
  const colorIndex = tournament.id % COLORS.length;

  return (
    <Link
      to={`/tournaments/${tournament.id}`}
      className={`block rounded-2xl p-5 ${COLORS[colorIndex]} hover:opacity-90 transition-opacity min-w-[220px]`}
    >
      <h3 className="text-text-primary text-xl font-semibold mb-1">{tournament.name}</h3>
      <p className="text-text-secondary text-sm mb-3">{tournament.sport}</p>
      <StatusBadge status={tournament.status} />
    </Link>
  );
}