import client from './client';

export function listParticipants(tournamentId) {
  return client.get(`/tournaments/${tournamentId}/participants`);
}

export function registerParticipant(tournamentId, payload) {
  return client.post(`/tournaments/${tournamentId}/participants`, payload);
}

export function removeParticipant(tournamentId, participantId) {
  return client.delete(`/tournaments/${tournamentId}/participants/${participantId}`);
}