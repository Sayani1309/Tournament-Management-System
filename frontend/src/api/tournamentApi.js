import client from './client';

export function listTournaments({ page = 1, perPage = 20, status } = {}) {
  const params = { page, per_page: perPage };
  if (status) params.status = status;
  return client.get('/tournaments', { params });
}

export function getTournament(id) {
  return client.get(`/tournaments/${id}`);
}

export function createTournament(payload) {
  return client.post('/tournaments', payload);
}

export function updateTournament(id, payload) {
  return client.put(`/tournaments/${id}`, payload);
}

export function openRegistration(id) {
  return client.post(`/tournaments/${id}/open-registration`);
}

export function startTournament(id) {
  return client.post(`/tournaments/${id}/start`);
}