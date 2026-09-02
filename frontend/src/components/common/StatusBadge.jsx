const STYLES = {
  DRAFT: 'bg-gray-600',
  REGISTRATION_OPEN: 'bg-emerald-700',
  ONGOING: 'bg-amber-600',
  COMPLETED: 'bg-slate-700',
};

const LABELS = {
  DRAFT: 'Draft',
  REGISTRATION_OPEN: 'Registration Open',
  ONGOING: 'Live',
  COMPLETED: 'Completed',
};

export default function StatusBadge({ status }) {
  return (
    <span className={`inline-block px-3 py-1 rounded-full text-xs font-medium text-text-primary ${STYLES[status] || 'bg-gray-600'}`}>
      {LABELS[status] || status}
    </span>
  );
}