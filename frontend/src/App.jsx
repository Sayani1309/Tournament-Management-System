import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import HomePage from './pages/HomePage';
import AuthLandingPage from './pages/AuthLandingPage';
import PlayerRegisterPage from './pages/PlayerRegisterPage';
import OrganizerRegisterPage from './pages/OrganizerRegisterPage';
import PlayerLoginPage from './pages/PlayerLoginPage';
import OrganizerLoginPage from './pages/OrganizerLoginPage';
import TournamentDetailPage from './pages/TournamentDetailPage';
import PlayerDashboardPage from './pages/PlayerDashboardPage';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/auth" element={<AuthLandingPage />} />
          <Route path="/player/register" element={<PlayerRegisterPage />} />
          <Route path="/organizer/register" element={<OrganizerRegisterPage />} />
          <Route path="/player/login" element={<PlayerLoginPage />} />
          <Route path="/organizer/login" element={<OrganizerLoginPage />} />
          <Route path="/tournaments/:id" element={<TournamentDetailPage />} />
          <Route path="/player/dashboard" element={<PlayerDashboardPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;