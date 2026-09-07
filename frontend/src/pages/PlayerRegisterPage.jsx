import Card from '../components/common/Card';
import PlayerRegisterForm from '../components/auth/PlayerRegisterForm';

export default function PlayerRegisterPage() {
  return (
    <div className="app-gradient-bg flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Player Sign Up</h1>
        <PlayerRegisterForm />
      </Card>
    </div>
  );
}