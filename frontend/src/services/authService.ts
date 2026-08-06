/**
 * Authentication API Client Service.
 *
 * Encapsulates HTTP calls for identity, registration, and session endpoints.
 */

import { api } from './api';

export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: 'patient' | 'clinician' | 'researcher' | 'administrator' | 'admin';
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export const authService = {
  async register(data: Record<string, unknown>): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  async login(credentials: Record<string, unknown>): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>('/auth/login', credentials);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  async logout(): Promise<void> {
    await api.post('/auth/logout');
  },
};