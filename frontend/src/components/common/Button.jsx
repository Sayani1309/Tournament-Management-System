export default function Button({ children, variant = 'primary', className = '', ...props }) {
  const base = 'px-6 py-2 rounded-full font-medium transition-opacity hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed';
  const variants = {
    primary: 'bg-accent text-text-primary',
    secondary: 'bg-card text-text-primary border border-accent',
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}