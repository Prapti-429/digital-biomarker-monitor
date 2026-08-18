import axios, { AxiosInstance } from 'axios';

const configuredURL = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const fallbackURL = 'https://digital-biomarker-backend.onrender.com/api/v1';

const normalizeBaseURL = (value: string): string => {
  const url = (value || fallbackURL).replace(/\/+$/, '');
  const withoutDuplicates = url.replace(/(\/api\/v1)+$/i, '');
  return `${withoutDuplicates}/api/v1`;
};

const baseURL = normalizeBaseURL(configuredURL);

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('nuvyra_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('nuvyra_token');
    }
    return Promise.reject(error);
  }
);

export const api = apiClient;

export const systemApi = {
  getRoot: async () => (await axios.get(baseURL.replace(/\/api\/v1$/i, '/'))).data,
  getHealth: async () => (await axios.get(`${baseURL.replace(/\/api\/v1$/i, '')}/health`, { timeout: 60000 })).data,
  getHealthStatus: async () => (await axios.get(`${baseURL.replace(/\/api\/v1$/i, '')}/health`, { timeout: 60000 })).data,
};

export default apiClient;
