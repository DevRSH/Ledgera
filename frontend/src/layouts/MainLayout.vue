<script setup lang="ts">
import { useAuthStore } from '../stores/auth.store';
import { useRouter } from 'vue-router';

import { ref } from 'vue';

const authStore = useAuthStore();
const router = useRouter();

const isSidebarOpen = ref(false);

function handleLogout() {
  authStore.logout();
  router.push('/login');
}
</script>

<template>
  <div class="min-h-screen bg-slate-950 flex flex-col md:flex-row">
    
    <!-- Mobile Header -->
    <header class="md:hidden flex items-center justify-between p-4 bg-slate-900 border-b border-slate-800 z-40 sticky top-0">
      <h1 class="text-xl font-bold text-white tracking-tight">Ledgera</h1>
      <button @click="isSidebarOpen = !isSidebarOpen" class="text-slate-400 hover:text-white p-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" v-if="!isSidebarOpen"/>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" v-else/>
        </svg>
      </button>
    </header>

    <!-- Overlay for mobile -->
    <div v-if="isSidebarOpen" @click="isSidebarOpen = false" class="fixed inset-0 bg-slate-950/80 z-40 md:hidden backdrop-blur-sm"></div>

    <!-- Sidebar -->
    <aside 
      :class="[
        'fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 flex flex-col transform transition-transform duration-300 ease-in-out',
        isSidebarOpen ? 'translate-x-0' : '-translate-x-full',
        'md:relative md:translate-x-0'
      ]"
    >
      <div class="p-6 border-b border-slate-800 flex justify-between items-center">
        <h1 class="text-xl font-bold text-white tracking-tight">
          Ledgera
        </h1>
        <button @click="isSidebarOpen = false" class="md:hidden text-slate-400 hover:text-white">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <nav class="flex-1 p-4 space-y-2 overflow-y-auto">
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

        <router-link 
          to="/comunicaciones" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/comunicaciones') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">📧</span> Comunicaciones
        </router-link>

        <router-link 
          to="/reportes" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/reportes') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">📊</span> Reportes
        </router-link>

        <router-link 
          to="/auditoria" 
          class="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-all"
          :class="$route.path.startsWith('/auditoria') ? 'bg-primary-600 text-white shadow-lg shadow-primary-600/20' : 'text-slate-400 hover:bg-slate-800 hover:text-white'"
        >
          <span class="mr-3">🕵️</span> Auditoría
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
    <main class="flex-1 overflow-auto bg-slate-950 relative w-full">
      <router-view />
    </main>
  </div>
</template>
