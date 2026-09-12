import { createContext, useState, useEffect, useCallback } from 'react';
import { setUnauthorizedHandler } from '../api/client';
import { login as apiLogin, logout as apiLogout, getMe } from '../api/authApi';
import { getRoleFromToken } from '../utils/jwt';

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('tms_token'));
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const clearAuth = useCallback(() => {
    localStorage.removeItem('tms_token');
    setToken(null);
    setUser(null);
  }, []);

useEffect(() => {
  setUnauthorizedHandler(() => {
    clearAuth();
    if (window.location.pathname !== '/auth') {
      window.location.href = '/auth';
    }
  });
}, [clearAuth]);

  useEffect(() => {
    async function loadUser() {
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const res = await getMe();
        setUser(res.data);
      } catch {
        clearAuth();
      } finally {
        setLoading(false);
      }
    }
    loadUser();
  }, [token, clearAuth]);

  async function login(email, password) {
    const res = await apiLogin(email, password);
    const newToken = res.data.access_token;
    localStorage.setItem('tms_token', newToken);
    setToken(newToken);
    const me = await getMe();
    setUser(me.data);
    return me.data;
  }

  async function logout() {
    try {
      await apiLogout();
    } catch {
      // ignore — clear local state regardless
    }
    clearAuth();
  }

  const role = token ? getRoleFromToken(token) : null;

  const value = {
    token,
    user,
    role,
    isAuthenticated: !!token && !!user,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}