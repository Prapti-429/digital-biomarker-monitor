import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';

const configuredURL = String(import.meta.env.VITE_API_BASE_URL || '').trim();
const fallbackURL = 'https://digital-biomarker-backend.onrender.com/api/v1';

const normalizeBaseURL = (value: string): string => {
  const raw = (value || fallbackURL).trim().replace(/\/+$/, '');
  const withoutDuplicates = raw.replace(/(\/api\/v1)+$/i, '');
  return `${withoutDuplicates}/api/v1`;
};

export const baseURL = normalizeBaseURL(configuredURL);
const API_ORIGIN = baseURL.replace(/\/api\/v1$/i, '');
const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1200;

export interface CustomAxiosRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
  _retryCount?: number;
}

export interface ApiErrorResponse {
  error_code?: string;
  message?: string;
  detail?: string | unknown[];
  details?: Record<string, unknown>;
  timestamp?: string;
}

const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token') || localStorage.getItem('nuvyra_token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorResponse>) => {
    const originalRequest = error.config as CustomAxiosRequestConfig | undefined;
    if (!originalRequest) return Promise.reject(error);

    // One refresh attempt for expired authenticated sessions.
    if (error.response?.status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        originalRequest._retry = true;
        try {
          const refreshResponse = await axios.post(`${baseURL}/auth/refresh`, {
            refresh_token: refreshToken,
          }, { timeout: 30000 });
          const newAccessToken = refreshResponse.data?.access_token;
          const newRefreshToken = refreshResponse.data?.refresh_token;
          if (!newAccessToken) throw new Error('Refresh response did not contain an access token.');
          localStorage.setItem('access_token', newAccessToken);
          localStorage.setItem('nuvyra_token', newAccessToken);
          if (newRefreshToken) localStorage.setItem('refresh_token', newRefreshToken);
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
          return apiClient(originalRequest);
        } catch (refreshError) {
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('nuvyra_token');
          return Promise.reject(refreshError);
        }
      }
    }

    const isTransient = !error.response || error.response.status === 502 || error.response.status === 503 || error.response.status === 504 || (error.response.status >= 500 && error.response.status <= 599);
    originalRequest._retryCount = originalRequest._retryCount || 0;
    if (isTransient && originalRequest._retryCount < MAX_RETRIES) {
      originalRequest._retryCount += 1;
      await delay(INITIAL_RETRY_DELAY * Math.pow(2, originalRequest._retryCount - 1));
      return apiClient(originalRequest);
    }

    const responseData = error.response?.data;
    const detail = responseData?.detail;
    let message = responseData?.message || error.message || 'Unable to reach the backend.';
    if (typeof detail === 'string') message = detail;
    if (Array.isArray(detail)) message = detail.map((item: any) => item?.msg || String(item)).join(', ');

    return Promise.reject(Object.assign(new Error(message), {
      status: error.response?.status,
      code: responseData?.error_code || (error.response ? `HTTP_${error.response.status}` : 'NETWORK_ERROR'),
      details: responseData?.details || {},
      isNetworkError: !error.response,
    }));
  }
);

export const systemApi = {
  getRoot: async () => (await axios.get(`${API_ORIGIN}/`, { timeout: 30000 })).data,
  getHealth: async () => (await axios.get(`${API_ORIGIN}/health`, { timeout: 30000 })).data,
  getHealthStatus: async () => (await axios.get(`${API_ORIGIN}/health`, { timeout: 30000 })).data,
};

export const createCancellableRequest = <T>(requestFn: (signal: AbortSignal) => Promise<T>) => {
  const controller = new AbortController();
  const promise = requestFn(controller.signal);
  return { promise, cancel: () => controller.abort() };
};

export const api = apiClient;
export default apiClient;
