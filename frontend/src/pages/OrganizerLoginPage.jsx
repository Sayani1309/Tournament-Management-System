import Card from '../components/common/Card';
import LoginForm from '../components/auth/LoginForm';

export default function OrganizerLoginPage() {
  return (
    <div className="app-gradient-bg flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Organizer Log In</h1>
        <LoginForm expectedRole="ORGANIZER" onSuccessPath="/organizer/dashboard" />
      </Card>
    </div>
  );
}