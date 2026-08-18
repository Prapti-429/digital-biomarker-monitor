import axios, { AxiosInstance } from 'axios';

// Render frontend -> Render FastAPI backend.
// Keep the production URL as the fallback so the app works even when
// VITE_API_BASE_URL is not configured in Render.
const baseURL = (
  import.meta.env.VITE_API_BASE_URL ||
  'https://digital-biomarker-backend.onrender.com/api/v1'
).replace(/\/$/, '');

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 30000,
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
    const response = await axios.get(`${baseURL.replace(/\/api\/v1$/, '')}/`);
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
