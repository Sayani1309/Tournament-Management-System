import client from './client';

export function listPlayers(page = 1, perPage = 100) {
  return client.get('/players', { params: { page, per_page: perPage } });
}

export function getPlayer(id) {
  return client.get(`/players/${id}`);
}

export function updatePlayerTeam(id, teamId) {
  return client.put(`/players/${id}/team`, { team_id: teamId });
}

export function getPlayerProfile(id) {
  return client.get(`/players/${id}/profile`);
}