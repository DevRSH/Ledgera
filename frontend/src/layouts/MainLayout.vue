<script setup lang="ts">
import { useAuthStore } from '../stores/auth.store';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex">
    <!-- Sidebar -->
    <aside class="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
      <div class="p-6 border-b border-slate-800">
        <h1 class="text-xl font-bold text-white tracking-tight">
          Teso<span class="text-primary-500">App</span>
        </h1>
      </div>
      
      <nav class="flex-1 p-4 space-y-2">
        <router-link 
          to="/" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.name === 'Dashboard' ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">📊</span> Dashboard
        </router-link>
        
        <router-link 
          to="/alumnos" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/alumnos') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">👥</span> Alumnos
        </router-link>

        <router-link 
          to="/cuotas" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/cuotas') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">💰</span> Cuotas
        </router-link>

        <router-link 
          to="/movimientos" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/movimientos') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">💸</span> Movimientos
        </router-link>

        <router-link 
          to="/documentos" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/documentos') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">📂</span> Documentos
        </router-link>

      </nav>
      
      <div class="p-4 border-t border-slate-800">
        <div class="flex items-center px-4 py-2 text-slate-400">
          <div class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center mr-3 text-xs font-bold text-primary-500">
            {{ authStore.user?.nombre?.[0] || 'U' }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ authStore.user?.nombre || 'Usuario' }}</p>
            <p class="text-xs truncate uppercase">{{ authStore.user?.rol || 'Rol' }}</p>
          </div>
        </div>
        <button 
          @click="handleLogout"
          class="w-full mt-4 flex items-center px-4 py-2 rounded-lg text-sm font-medium text-red-400 hover:bg-red-500/10 transition-all"
        >
          <span class="mr-3">🚪</span> Cerrar Sesión
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 overflow-auto">
      <router-view />
    </main>
  </div>
</template>
