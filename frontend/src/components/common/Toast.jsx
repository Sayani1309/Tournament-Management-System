import { useEffect } from 'react';

export default function Toast({ message, onDismiss, duration = 3000 }) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(onDismiss, duration);
    return () => clearTimeout(timer);
  }, [message, onDismiss, duration]);

  if (!message) return null;

  return (
    <div className="fixed bottom-6 right-6 bg-accent text-text-primary rounded-2xl px-5 py-3 shadow-lg z-50 animate-[fadeIn_0.2s_ease-in]">
      {message}
    </div>
  );
}