export default function LoadingOverlay({ show }) {
  if (!show) return null;
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-40">
      <div className="w-12 h-12 border-4 border-text-secondary border-t-accent rounded-full animate-spin" />
    </div>
  );
}