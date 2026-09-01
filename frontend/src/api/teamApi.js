import client from './client';

export function listTeams(page = 1, perPage = 100) {
  return client.get('/teams', { params: { page, per_page: perPage } });
}

export function getTeam(id) {
  return client.get(`/teams/${id}`);
}