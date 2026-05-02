import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api';


export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref<string | null>('dummy-token-bypass');
  const user = ref<any>({ nombre: 'Admin (Bypass)', rol: 'SUPER_ADMIN' });
  const loading = ref(false);

  const isAuthenticated = computed(() => true);


  async function login(credentials: { email: string; password: any }) {
    loading.value = true;
    try {
      const response = await api.post('/auth/login', credentials);

      if (response.data.require_2fa) {
        return { require_2fa: true, sessionToken: response.data.session_token };
      }
      accessToken.value = response.data.access_token;
      // In a real app, we'd fetch user info here
      await fetchUser();
      return { success: true };
    } finally {
      loading.value = false;
    }
  }

  async function fetchUser() {
    if (!accessToken.value) return;
    try {
      const response = await api.get('/auth/me');
      user.value = response.data;

    } catch (error) {
      logout();
    }
  }

  function logout() {
    accessToken.value = null;
    user.value = null;
  }

  return {
    accessToken,
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    fetchUser
  };
});
