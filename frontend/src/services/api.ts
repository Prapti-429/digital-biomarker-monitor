import axios, { AxiosInstance } from 'axios';

/**
 * Resolve the backend URL defensively.
 * Render can provide VITE_API_BASE_URL from the dashboard as either the API
 * root or the versioned API root. Normalize both forms so we never generate
 * /api/v1/api/v1/... URLs.
 */
const configuredURL = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const fallbackURL = 'https://digital-biomarker-backend.onrender.com/api/v1';

const normalizeBaseURL = (value: string): string => {
  const url = (value || fallbackURL).replace(/\/+$/, '');

  // Remove accidental duplicate version prefixes.
  const withoutDuplicates = url.replace(/(\/api\/v1)+$/i, '');

  // The frontend API client always works relative to /api/v1.
  return `${withoutDuplicates}/api/v1`;
};

const baseURL = normalizeBaseURL(configuredURL);

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 45000,
});

apiClient.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem('access_token') || localStorage.getItem('nuvyra_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('nuvyra_token');
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export const api = apiClient;

export const systemApi = {
  getRoot: async () => {
    const response = await axios.get(baseURL.replace(/\/api\/v1$/i, '/'));
    return response.data;
  },
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
  getHealthStatus: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiClient;
