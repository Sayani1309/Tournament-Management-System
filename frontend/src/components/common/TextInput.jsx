export default function TextInput({ label, ...props }) {
  return (
    <div className="mb-4">
      {label && <label className="block text-text-secondary text-sm mb-1">{label}</label>}
      <input
        className="w-full bg-transparent border-b border-text-secondary text-text-primary py-2 outline-none focus:border-accent"
        {...props}
      />
    </div>
  );
}