<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';

const historial = ref<any[]>([]);
const loading = ref(true);

async function fetchHistorial() {
  loading.value = true;
  try {
    const response = await api.get('/v1/comunicaciones/historial');
    historial.value = response.data;
  } catch (error) {
    console.error('Error fetching communication history:', error);
  } finally {
    loading.value = false;
  }
}

function getStatusClass(estado: string) {
  switch (estado) {
    case 'enviado': return 'bg-green-500/10 text-green-500';
    case 'fallido': return 'bg-red-500/10 text-red-500';
    case 'pendiente': return 'bg-yellow-500/10 text-yellow-500';
    default: return 'bg-slate-500/10 text-slate-500';
  }
}

onMounted(fetchHistorial);
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <header>
      <h1 class="text-3xl font-bold text-white">Comunicaciones</h1>
      <p class="text-slate-400">Historial de correos enviados a apoderados</p>
    </header>

    <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th class="px-6 py-3 font-medium">Fecha</th>
              <th class="px-6 py-3 font-medium">Destinatario</th>
              <th class="px-6 py-3 font-medium">Asunto</th>
              <th class="px-6 py-3 font-medium text-center">Estado</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <tr v-for="item in historial" :key="item.id" class="hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4 text-sm text-slate-400">{{ new Date(item.created_at).toLocaleString() }}</td>
              <td class="px-6 py-4 text-sm">
                <p class="text-white font-medium">{{ item.destinatario_nombre }}</p>
                <p class="text-xs text-slate-500">{{ item.destinatario_email }}</p>
              </td>
              <td class="px-6 py-4 text-sm text-slate-300">{{ item.asunto }}</td>
              <td class="px-6 py-4 text-sm text-center">
                <span :class="getStatusClass(item.estado)" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ item.estado }}
                </span>
              </td>
            </tr>
            <tr v-if="historial.length === 0" class="text-center">
              <td colspan="4" class="px-6 py-12 text-slate-500">No se han enviado correos todavía</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
