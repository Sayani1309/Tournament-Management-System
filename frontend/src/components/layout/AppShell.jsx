import Sidebar from './Sidebar';

export default function AppShell({ children }) {
  return (
    <div className="min-h-screen bg-bg-primary">
      <Sidebar />
      <div className="ml-20 p-8">
        {children}
      </div>
    </div>
  );
}