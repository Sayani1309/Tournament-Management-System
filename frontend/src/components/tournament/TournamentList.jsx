import TournamentCard from './TournamentCard';
import EmptyState from '../common/EmptyState';

export default function TournamentList({ tournaments }) {
  if (!tournaments || tournaments.length === 0) {
    return <EmptyState message="No tournaments found." />;
  }
  return (
    <div className="flex gap-4 overflow-x-auto pb-2">
      {tournaments.map((t, i) => (
        <TournamentCard key={t.id} tournament={t} colorIndex={i} />
      ))}
    </div>
  );
}