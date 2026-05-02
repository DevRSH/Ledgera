<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../../stores/auth.store';
import { useRouter, useRoute } from 'vue-router';
import api from '../../services/api';


const code = ref('');
const error = ref('');
const loading = ref(false);

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const sessionToken = route.query.sessionToken as string;

async function handleVerify() {
  error.value = '';
  loading.value = true;
  try {
    const response = await api.post('/v1/auth/login/2fa', {

      session_token: sessionToken,
      totp_code: code.value
    });
    
    authStore.accessToken = response.data.access_token;
    await authStore.fetchUser();
    router.push({ name: 'Dashboard' });
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Código inválido';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-950 p-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-white tracking-tight">
          Ledgera <span class="text-primary-500">2FA</span>
        </h1>
        <p class="text-slate-400 mt-2">Introduce el código de tu aplicación de autenticación</p>
      </div>


      <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-xl">
        <div class="p-8">
          <form @submit.prevent="handleVerify" class="space-y-6">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-4 text-center">Código de Verificación</label>
              <input 
                v-model="code"
                type="text" 
                required
                maxlength="6"
                class="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-4 text-center text-3xl tracking-[1em] text-white focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all font-mono"
                placeholder="000000"
              />
            </div>

            <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm text-center">
              {{ error }}
            </div>

            <button 
              type="submit"
              :disabled="loading || code.length < 6"
              class="w-full bg-primary-600 hover:bg-primary-500 text-white font-semibold py-3 rounded-lg shadow-lg shadow-primary-600/20 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="animate-spin mr-2">◌</span>
              {{ loading ? 'Verificando...' : 'Verificar Código' }}
            </button>
          </form>
        </div>
      </div>
      
      <button @click="router.push('/login')" class="w-full mt-6 text-slate-500 hover:text-slate-400 text-sm font-medium transition-colors">
        ← Volver al login
      </button>
    </div>
  </div>
</template>
