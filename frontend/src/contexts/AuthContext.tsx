import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiClient } from '../services/api';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  role?: string;
  is_active: boolean;
  subject_anonymous_id?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const loadCurrentUser = async (): Promise<User> => {
  const response = await apiClient.get('/auth/me');
  return response.data as User;
};

const decodeAccessTokenUser = (accessToken: string): User | null => {
  try {
    const payloadPart = accessToken.split('.')[1];
    if (!payloadPart) return null;
    const normalized = payloadPart.replace(/-/g, '+').replace(/_/g, '/');
    const padded = normalized.padEnd(normalized.length + ((4 - (normalized.length % 4)) % 4), '=');
    const payload = JSON.parse(window.atob(padded)) as {
      sub?: string;
      role?: string;
    };
    if (!payload.sub) return null;
    return {
      id: payload.sub,
      email: '',
      role: payload.role || 'patient',
      is_active: true,
    };
  } catch {
    return null;
  }
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('nuvyra_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('nuvyra_token');
      if (storedToken) {
        try {
          const currentUser = await loadCurrentUser();
          setUser(currentUser);
          setToken(storedToken);
        } catch {
          localStorage.removeItem('nuvyra_token');
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const normalizedEmail = email.trim().toLowerCase();
    const response = await apiClient.post('/auth/login', {
      email: normalizedEmail,
      password,
    });
    const { access_token, refresh_token, user: authenticatedUser } = response.data || {};

    if (!access_token) {
      throw new Error('The server did not return a valid access token.');
    }

    localStorage.setItem('nuvyra_token', access_token);
    localStorage.setItem('access_token', access_token);
    if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
    setToken(access_token);

    // The login response now includes the authenticated profile, so the UI
    // does not depend on a second request before considering login successful.
    if (authenticatedUser?.id) {
      setUser(authenticatedUser as User);
    }

    try {
      const currentUser = await loadCurrentUser();
      setUser(currentUser);
    } catch {
      // Login itself succeeded and the access token is valid. Do not turn a
      // secondary /auth/me/profile failure into a false "authentication failed"
      // message. The token can still protect API requests, and the normal auth
      // bootstrap will retry the profile request on the next page load.
      const tokenUser = decodeAccessTokenUser(access_token);
      if (tokenUser) {
        setUser(tokenUser);
        return;
      }
      throw new Error('Signed in, but the session profile could not be loaded. Please refresh and try again.');
    }
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const response = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });

    const registeredUser = response.data as User;
    if (!registeredUser?.id) {
      throw new Error('Account was created but the server returned an invalid user record.');
    }

    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('nuvyra_token');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, token, isAuthenticated: !!token, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
