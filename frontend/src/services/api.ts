import axios, { AxiosInstance, AxiosError } from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    // Structural boundary left open for future authentication injection tasks
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const errorDetails = {
      message: error.message,
      status: error.response?.status,
      url: error.config?.url,
    };
    console.error('API Infrastructure Layer Disconnected:', errorDetails);
    return Promise.reject(error);
  }
);

export const systemApi = {
  getRoot: async () => {
    const response = await apiClient.get('/');
    return response.data;
  },
  getHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },
};