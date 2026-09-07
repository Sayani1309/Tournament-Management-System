import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/layout/ProtectedRoute';
import HomePage from './pages/HomePage';
import AuthLandingPage from './pages/AuthLandingPage';
import PlayerRegisterPage from './pages/PlayerRegisterPage';
import OrganizerRegisterPage from './pages/OrganizerRegisterPage';
import PlayerLoginPage from './pages/PlayerLoginPage';
import OrganizerLoginPage from './pages/OrganizerLoginPage';
import TournamentDetailPage from './pages/TournamentDetailPage';
import MatchScoreCardPage from './pages/MatchScoreCardPage';
import PlayerDashboardPage from './pages/PlayerDashboardPage';
import OrganizerDashboardPage from './pages/OrganizerDashboardPage';
import CreateTournamentPage from './pages/CreateTournamentPage';
import TournamentManagementPage from './pages/TournamentManagementPage';
import MatchResultPage from './pages/MatchResultPage';
import StandingsPage from './pages/StandingsPage';
import VenueListPage from './pages/VenueListPage';
import CreateVenuePage from './pages/CreateVenuePage';
import NotFoundPage from './pages/NotFoundPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import PlayerTeamSettingsPage from './pages/PlayerTeamSettingsPage';
import PlayerProfilePage from './pages/PlayerProfilePage';
import TeamRosterPage from './pages/TeamRosterPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<HomePage />} />
          <Route path="/auth" element={<AuthLandingPage />} />
          <Route path="/player/register" element={<PlayerRegisterPage />} />
          <Route path="/organizer/register" element={<OrganizerRegisterPage />} />
          <Route path="/player/login" element={<PlayerLoginPage />} />
          <Route path="/organizer/login" element={<OrganizerLoginPage />} />
          <Route path="/tournaments/:id" element={<TournamentDetailPage />} />
          <Route path="/tournaments/:id/standings" element={<StandingsPage />} />
          <Route path="/matches/:id" element={<MatchScoreCardPage />} />
          <Route path="/venues" element={<VenueListPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/players/:id/profile" element={<PlayerProfilePage />} />
          <Route path="/teams/:id/roster" element={<TeamRosterPage />} />
          
          {/* Player-only routes */}
          <Route
            path="/player/dashboard"
            element={
              <ProtectedRoute requiredRole="PLAYER">
                <PlayerDashboardPage />
              </ProtectedRoute>
            }
          />

          {/* Organizer-only routes */}
          <Route
            path="/organizer/dashboard"
            element={
              <ProtectedRoute requiredRole="ORGANIZER">
                <OrganizerDashboardPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/organizer/tournaments/new"
            element={
              <ProtectedRoute requiredRole="ORGANIZER">
                <CreateTournamentPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/organizer/tournaments/:id"
            element={
              <ProtectedRoute requiredRole="ORGANIZER">
                <TournamentManagementPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/organizer/matches/:id/result"
            element={
              <ProtectedRoute requiredRole="ORGANIZER">
                <MatchResultPage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/venues/new"
            element={
              <ProtectedRoute requiredRole="ORGANIZER">
                <CreateVenuePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/player/team-settings"
            element={
              <ProtectedRoute requiredRole="PLAYER">
                <PlayerTeamSettingsPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;