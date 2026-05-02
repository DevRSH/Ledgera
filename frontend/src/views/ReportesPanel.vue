<script setup lang="ts">
import { ref } from 'vue';
import api from '../services/api';

const loading = ref(false);

async function downloadDeudores() {
  loading.value = true;
  try {
    const response = await api.post('/reportes/nomina-deudores/export', {}, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'nomina_deudores.xlsx');
    document.body.appendChild(link);
    link.click();
    link.remove();
  } catch (error) {
    console.error('Error downloading report:', error);
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-8">
    <header>
      <h1 class="text-3xl font-bold text-white">Reportes y Auditoría</h1>
      <p class="text-slate-400">Genera informes financieros y nóminas de control</p>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Card: Nómina de Deudores -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-primary-500/30 transition-colors group">
        <div class="flex items-start justify-between mb-6">
          <div class="p-3 bg-slate-950 rounded-xl text-red-500">
            📊
          </div>
          <span class="text-xs font-mono text-slate-500">EXCEL</span>
        </div>
        <h2 class="text-xl font-bold text-white mb-2">Nómina de Deudores</h2>
        <p class="text-slate-400 text-sm mb-6">
          Lista completa de alumnos con cuotas pendientes, incluyendo datos de contacto del apoderado.
        </p>
        <button 
          @click="downloadDeudores"
          :disabled="loading"
          class="w-full bg-slate-800 hover:bg-primary-600 text-white font-medium py-2.5 rounded-lg transition-all flex items-center justify-center gap-2"
        >
          <span v-if="loading">Generando...</span>
          <span v-else>Descargar Excel</span>
        </button>
      </div>

      <!-- Card: Balance Mensual -->
      <div class="bg-slate-900 border border-slate-800 rounded-2xl p-6 hover:border-primary-500/30 transition-colors group">
        <div class="flex items-start justify-between mb-6">
          <div class="p-3 bg-slate-950 rounded-xl text-primary-500">
            ⚖️
          </div>
          <span class="text-xs font-mono text-slate-500">PDF</span>
        </div>
        <h2 class="text-xl font-bold text-white mb-2">Balance Mensual</h2>
        <p class="text-slate-400 text-sm mb-6">
          Resumen ejecutivo de ingresos y egresos del mes actual con saldo final.
        </p>
        <button class="w-full bg-slate-800 hover:bg-primary-600 text-white font-medium py-2.5 rounded-lg transition-all">
          Generar PDF
        </button>
      </div>
    </div>
  </div>
</template>
