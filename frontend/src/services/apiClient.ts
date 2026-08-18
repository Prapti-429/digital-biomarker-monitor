// Compatibility facade: the application now uses one production API client.
// Keep this module so existing imports continue to work without maintaining
// a second base URL, retry policy, auth interceptor, or refresh implementation.
export {
  apiClient,
  apiClient as default,
  api,
  baseURL,
  systemApi,
  createCancellableRequest,
} from './api';

export type { CustomAxiosRequestConfig, ApiErrorResponse } from './api';
