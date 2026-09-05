import client from './client';

export function listVenues() {
  return client.get('/venues');
}

export function createVenue(payload) {
  return client.post('/venues', payload);
}