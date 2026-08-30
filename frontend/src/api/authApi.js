import client from './client';

export function register(payload) {
  return client.post('/auth/register', payload);
}

export function login(email, password) {
  return client.post('/auth/login', { email, password });
}

export function logout() {
  return client.post('/auth/logout');
}

export function getMe() {
  return client.get('/auth/me');
}

export function getMyTournaments() {
  return client.get('/auth/me/tournaments');
}

export function forgotPassword(email) {
  return client.post('/auth/forgot-password', { email });
}

export function resetPassword(token, newPassword) {
  return client.post('/auth/reset-password', { token, new_password: newPassword });
}

export function verifyEmail(token) {
  return client.get(`/auth/verify-email?token=${encodeURIComponent(token)}`);
}