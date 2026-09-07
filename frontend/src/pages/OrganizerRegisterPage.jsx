import Card from '../components/common/Card';
import OrganizerRegisterForm from '../components/auth/OrganizerRegisterForm';

export default function OrganizerRegisterPage() {
  return (
    <div className="app-gradient-bg flex items-center justify-center p-8">
      <Card className="w-full max-w-md">
        <h1 className="text-2xl text-text-primary mb-6">Organizer Sign Up</h1>
        <OrganizerRegisterForm />
      </Card>
    </div>
  );
}