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
    const response = await apiClient.post('/auth/login', { email, password });
    const { access_token } = response.data;

    if (!access_token) {
      throw new Error('Login succeeded but the server did not return an access token.');
    }

    localStorage.setItem('nuvyra_token', access_token);
    localStorage.setItem('access_token', access_token);
    setToken(access_token);

    // Login returns tokens only. Fetch the authenticated user separately.
    const currentUser = await loadCurrentUser();
    setUser(currentUser);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    // Registration returns UserRead, not JWT tokens. Authenticate immediately
    // afterwards so the newly-created user is taken directly into the app.
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
