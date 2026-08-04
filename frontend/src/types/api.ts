export type ConnectionStatus = 'LOADING' | 'CONNECTED' | 'UNAVAILABLE';

export interface BaseApiResponse {
  message: string;
  status: string;
}

export interface HealthApiResponse {
  status: string;
  timestamp: string;
  version: string;
  uptime?: number;
}