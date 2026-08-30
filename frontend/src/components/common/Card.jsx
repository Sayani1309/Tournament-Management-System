export default function Card({ children, className = '' }) {
  return (
    <div className={`bg-card rounded-3xl p-8 shadow-lg ${className}`}>
      {children}
    </div>
  );
}