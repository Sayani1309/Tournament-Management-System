export default function EmptyState({ message = 'Nothing here yet.' }) {
  return (
    <div className="text-text-secondary text-center py-12">
      {message}
    </div>
  );
}