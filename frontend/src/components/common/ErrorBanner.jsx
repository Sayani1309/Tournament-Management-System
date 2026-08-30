export default function ErrorBanner({ message }) {
  if (!message) return null;
  return (
    <div className="bg-accent-dark text-text-primary rounded-xl px-4 py-3 mb-4 text-sm">
      {message}
    </div>
  );
}