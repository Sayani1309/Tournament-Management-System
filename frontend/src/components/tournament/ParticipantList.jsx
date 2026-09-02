import EmptyState from '../common/EmptyState';

export default function ParticipantList({ participants }) {
  if (!participants || participants.length === 0) {
    return <EmptyState message="No participants registered yet." />;
  }
  return (
    <div className="flex flex-col gap-2">
      {participants.map((p) => (
        <div key={p.id} className="bg-card rounded-xl px-4 py-3 text-text-primary flex justify-between">
          <span>{p.participant?.name || 'Unknown'}</span>
          <span className="text-text-secondary text-sm">{p.participant?.type}</span>
        </div>
      ))}
    </div>
  );
}