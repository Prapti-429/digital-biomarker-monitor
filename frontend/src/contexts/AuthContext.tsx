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

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('nuvyra_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const storedToken = localStorage.getItem('nuvyra_token');
      if (storedToken) {
        try {
          const response = await apiClient.get('/api/v1/auth/me');
          setUser(response.data);
          setToken(storedToken);
        } catch {
          localStorage.removeItem('nuvyra_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/api/v1/auth/login', { email, password });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('nuvyra_token', access_token);
    setToken(access_token);
    setUser(userData);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const response = await apiClient.post('/api/v1/auth/register', { email, password, full_name: fullName });
    const { access_token, user: userData } = response.data;

    localStorage.setItem('nuvyra_token', access_token);
    setToken(access_token);
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('nuvyra_token');
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
