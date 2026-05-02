import axios from 'axios';

let baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// Limpieza automática de /v1 duplicados
if (baseUrl.endsWith('/v1')) {
  baseUrl = baseUrl.slice(0, -3);
}

const api = axios.create({
  baseURL: `${baseUrl}/v1`,
});


api.interceptors.request.use(async (config) => {
  // Dynamic import to avoid circular dependency
  const { useAuthStore } = await import('../stores/auth.store');
  const authStore = useAuthStore();
  
  if (authStore.accessToken) {
    config.headers.Authorization = `Bearer ${authStore.accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const { useAuthStore } = await import('../stores/auth.store');
      const authStore = useAuthStore();
      authStore.logout();
      // Handle redirect to login if needed
    }
    return Promise.reject(error);
  }
);

export default api;
