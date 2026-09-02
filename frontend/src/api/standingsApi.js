import client from './client';

export function getStandings(tournamentId) {
  return client.get(`/tournaments/${tournamentId}/standings`);
}