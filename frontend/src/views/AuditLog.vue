<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';

const logs = ref([]);
const loading = ref(false);

async function fetchLogs() {
  loading.value = true;
  try {
    const response = await api.get('/v1/auditoria/log');
    logs.value = response.data;
  } catch (error) {
    console.error('Error fetching logs:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchLogs);

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString();
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-8">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-white">Log de Auditoría</h1>
        <p class="text-slate-400">Historial inmutable de acciones en el sistema</p>
      </div>
      <button 
        @click="fetchLogs"
        class="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-white transition-colors"
      >
        🔄 Actualizar
      </button>
    </header>

    <div class="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-950/50 text-slate-400 text-xs font-mono uppercase tracking-wider">
            <tr>
              <th class="px-6 py-4">Fecha</th>
              <th class="px-6 py-4">Acción</th>
              <th class="px-6 py-4">Entidad</th>
              <th class="px-6 py-4">IP</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <tr v-if="loading">
               <td colspan="4" class="px-6 py-12 text-center text-slate-500">Cargando registros...</td>
            </tr>
            <tr v-else-if="logs.length === 0">
               <td colspan="4" class="px-6 py-12 text-center text-slate-500">No hay registros de auditoría</td>
            </tr>
            <tr 
              v-for="log in logs" 
              :key="log.id"
              class="hover:bg-slate-800/30 transition-colors group"
            >
              <td class="px-6 py-4 text-sm text-slate-300">
                {{ formatDate(log.created_at) }}
              </td>
              <td class="px-6 py-4">
                <span class="px-2 py-1 bg-primary-500/10 text-primary-400 rounded text-xs font-medium uppercase">
                  {{ log.accion }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-slate-400">
                {{ log.entidad_tipo }} <span class="text-slate-600 text-xs">#{{ log.entidad_id }}</span>
              </td>
              <td class="px-6 py-4 text-xs font-mono text-slate-500">
                {{ log.ip_address }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
