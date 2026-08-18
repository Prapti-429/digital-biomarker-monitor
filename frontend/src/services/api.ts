import axios, { AxiosInstance } from 'axios';

// The frontend is deployed as a Render Static Site, while FastAPI runs as a
// separate Render Web Service. Use the public backend URL unless Render
// explicitly provides VITE_API_BASE_URL at build time.
const baseURL =
  import.meta.env.VITE_API_BASE_URL ||
  'https://digital-biomarker-backend.onrender.com/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
  timeout: 15000,
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
    if (error.response && error.response.status === 401) {
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
    const response = await axios.get(baseURL.replace(/\/api\/v1$/, '') + '/');
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
