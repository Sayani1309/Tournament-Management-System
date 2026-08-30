import { useNavigate } from 'react-router-dom';
import Card from '../common/Card';
import Button from '../common/Button';

export default function RoleSelectCard({ title, signUpPath, loginPath }) {
  const navigate = useNavigate();
  return (
    <Card className="flex items-center justify-between gap-8">
      <div className="w-20 h-20 rounded-full border-2 border-text-primary flex items-center justify-center shrink-0">
        <svg viewBox="0 0 24 24" fill="currentColor" className="w-10 h-10 text-text-primary">
          <circle cx="12" cy="8" r="4" />
          <path d="M4 20c0-4 4-6 8-6s8 2 8 6" />
        </svg>
      </div>
      <h2 className="text-3xl text-text-primary flex-1">{title}</h2>
      <div className="flex flex-col items-center gap-1">
        <Button onClick={() => navigate(signUpPath)}>Sign Up</Button>
        <span className="text-xs text-text-secondary">New?</span>
      </div>
      <div className="flex flex-col items-center gap-1">
        <Button variant="secondary" onClick={() => navigate(loginPath)}>Log in</Button>
        <span className="text-xs text-text-secondary">Already!</span>
      </div>
    </Card>
  );
}