import { Link } from 'react-router-dom';
import EmptyState from '../common/EmptyState';
import StatusBadge from '../common/StatusBadge';

function formatSchedule(scheduledAt) {
  if (!scheduledAt) return null;
  return new Date(scheduledAt).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
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

export default function MatchList({ matches, venues = [] }) {
  if (!matches || matches.length === 0) {
    return <EmptyState message="Fixtures haven't been generated yet." />;
  }

  const venueName = (venueId) => venues.find((v) => v.id === venueId)?.name;

  return (
    <div className="flex flex-col gap-2">
      {matches.map((m) => {
        const venue = venueName(m.venue_id);
        const schedule = formatSchedule(m.scheduled_at);
        return (
          <Link
            key={m.id}
            to={`/matches/${m.id}`}
            className="bg-card rounded-xl px-4 py-3 flex justify-between items-center hover:opacity-90"
          >
            <div>
              <div className="text-text-secondary text-xs mb-1">{m.round}</div>
              <div className="text-text-primary">
                {m.participants.length === 2 ? (
                  <>
                    <ParticipantLink p={m.participants[0]} /> vs <ParticipantLink p={m.participants[1]} />
                  </>
                ) : m.participants.length === 1 ? (
                  <>
                    <ParticipantLink p={m.participants[0]} /> vs TBA
                  </>
                ) : (
                  'TBA vs TBA'
                )}
              </div>
              {(venue || schedule) && (
                <div className="text-text-secondary text-xs mt-1">
                  {venue && <span>📍 {venue}</span>}
                  {venue && schedule && <span className="mx-2">·</span>}
                  {schedule && <span>🕒 {schedule}</span>}
                </div>
              )}
            </div>
            <StatusBadge status={m.status} />
          </Link>
        );
      })}
    </div>
  );
}