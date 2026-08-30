import { jwtDecode } from 'jwt-decode';

export function decodeToken(token) {
  if (!token) return null;
  try {
    return jwtDecode(token);
  } catch {
    return null;
  }
}

export function getRoleFromToken(token) {
  const decoded = decodeToken(token);
  return decoded?.role || null;
}