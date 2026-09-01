import Card from '../components/common/Card';
import LoginForm from '../components/auth/LoginForm';

export default function PlayerLoginPage() {
  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Player Log In</h1>
        <LoginForm expectedRole="PLAYER" onSuccessPath="/player/dashboard" />
      </Card>
    </div>
  );
}