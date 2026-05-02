<script setup lang="ts">
import { ref } from 'vue';
import { useAuthStore } from '../../stores/auth.store';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const error = ref('');
const loading = ref(false);

const authStore = useAuthStore();
const router = useRouter();

async function handleLogin() {
  error.value = '';
  loading.value = true;
  try {
    const result = await authStore.login({ email: email.value, password: password.value });
    if (result?.require_2fa) {
      router.push({ name: 'Login2FA', query: { sessionToken: result.sessionToken } });
    } else {
      router.push({ name: 'Dashboard' });
    }
  } catch (err: any) {
    error.value = err.response?.data?.detail || 'Error al iniciar sesión';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen w-full flex items-center justify-center bg-slate-950 p-4">
    <div class="w-full max-w-md">
      <!-- Logo/Branding -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-white tracking-tight">
          Ledgera
        </h1>
        <p class="text-slate-400 mt-2">Todo claro. Todo bajo control.</p>
      </div>


      <!-- Login Card -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden backdrop-blur-xl">
        <div class="p-8">
          <h2 class="text-xl font-semibold text-white mb-6">Iniciar Sesión</h2>
          
          <form @submit.prevent="handleLogin" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-1.5">Correo Electrónico</label>
              <input 
                v-model="email"
                type="email" 
                required
                class="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder="ejemplo@correo.com"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-slate-300 mb-1.5">Contraseña</label>
              <input 
                v-model="password"
                type="password" 
                required
                class="w-full bg-slate-950 border border-slate-700 rounded-lg px-4 py-2.5 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-500/50 focus:border-primary-500 transition-all"
                placeholder="••••••••"
              />
            </div>

            <div v-if="error" class="bg-red-500/10 border border-red-500/20 text-red-400 px-4 py-2 rounded-lg text-sm">
              {{ error }}
            </div>

            <button 
              type="submit"
              :disabled="loading"
              class="w-full bg-primary-600 hover:bg-primary-500 text-white font-semibold py-2.5 rounded-lg shadow-lg shadow-primary-600/20 transition-all flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="loading" class="animate-spin mr-2">◌</span>
              {{ loading ? 'Iniciando...' : 'Entrar' }}
            </button>
          </form>
        </div>
        
        <div class="px-8 py-4 bg-slate-950/50 border-t border-slate-800 text-center">
          <p class="text-sm text-slate-500">
            ¿Problemas para entrar? 
            <a href="#" class="text-primary-500 hover:text-primary-400 font-medium">Contacta al administrador</a>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
