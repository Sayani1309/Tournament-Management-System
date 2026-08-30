import RoleSelectCard from '../components/auth/RoleSelectCard';

export default function AuthLandingPage() {
  return (
    <div className="min-h-screen bg-bg-primary flex items-center justify-center p-8">
      <div className="w-full max-w-2xl flex flex-col gap-8">
        <RoleSelectCard
          title="Player"
          signUpPath="/player/register"
          loginPath="/player/login"
        />
        <RoleSelectCard
          title="Organizer"
          signUpPath="/organizer/register"
          loginPath="/organizer/login"
        />
      </div>
    </div>
  );
}