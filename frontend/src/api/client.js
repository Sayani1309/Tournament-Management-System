import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';

const client = axios.create({ baseURL });

let onUnauthorized = null;
export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler;
}

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('tms_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('tms_token');
      if (onUnauthorized) onUnauthorized();
    }
    return Promise.reject(error);
  }
);

export default client;