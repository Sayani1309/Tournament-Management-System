import client from './client';

export function listMatches(tournamentId) {
  return client.get(`/tournaments/${tournamentId}/matches`);
}

export function getMatch(matchId) {
  return client.get(`/matches/${matchId}`);
}

export function generateFixtures(tournamentId) {
  return client.post(`/tournaments/${tournamentId}/fixtures`);
}

export function submitResult(matchId, payload) {
  return client.post(`/matches/${matchId}/result`, payload);
}

export function getResult(matchId) {
  return client.get(`/matches/${matchId}/result`);
}