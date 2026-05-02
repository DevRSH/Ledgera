import axios from 'axios';
import { useAuthStore } from '../stores/auth.store';

let baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Limpieza automática de /v1 duplicados
if (baseUrl.endsWith('/v1')) {
  baseUrl = baseUrl.slice(0, -3);
}

const api = axios.create({
  baseURL: `${baseUrl}/v1`,
});


api.interceptors.request.use((config) => {
  const authStore = useAuthStore();
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const authStore = useAuthStore();
    if (error.response?.status === 401) {
      authStore.logout();
      // Handle redirect to login if needed
    }
    return Promise.reject(error);
  }
);

export default api;
