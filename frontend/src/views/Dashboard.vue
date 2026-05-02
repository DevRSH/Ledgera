<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';

const saldo = ref(0);
const loading = ref(true);
const movimientos = ref<any[]>([]);

async function fetchData() {
  loading.value = true;
  try {
    const [saldoRes, movsRes] = await Promise.all([
      api.get('/movimientos/saldo'),
      api.get('/movimientos/')
    ]);
    saldo.value = saldoRes.data.saldo;
    movimientos.value = movsRes.data.data || [];
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
  } finally {
    loading.value = false;
  }
}

function formatCurrency(value: number) {
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(value);
}

onMounted(fetchData);
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <header class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-bold text-white">Dashboard</h1>
        <p class="text-slate-400">Resumen financiero del curso</p>
      </div>
      <button @click="fetchData" class="text-primary-500 hover:text-primary-400 text-sm font-medium">
        Actualizar datos
      </button>
    </header>

    <!-- Stat Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-sm">
        <p class="text-slate-400 text-sm font-medium mb-1">Saldo Disponible</p>
        <h2 class="text-3xl font-bold text-white tracking-tight" :class="saldo >= 0 ? 'text-green-400' : 'text-red-400'">
          {{ formatCurrency(saldo) }}
        </h2>
        <div class="mt-4 flex items-center text-xs text-slate-500">
          <span class="bg-green-500/10 text-green-500 px-2 py-0.5 rounded-full mr-2">Actualizado</span>
          <span>Hace un momento</span>
        </div>
      </div>

      <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-sm">
        <p class="text-slate-400 text-sm font-medium mb-1">Ingresos del Mes</p>
        <h2 class="text-3xl font-bold text-white tracking-tight">$0</h2>
        <p class="text-xs text-slate-500 mt-4 italic">Cálculo mensual pendiente</p>
      </div>

      <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-sm">
        <p class="text-slate-400 text-sm font-medium mb-1">Egresos del Mes</p>
        <h2 class="text-3xl font-bold text-white tracking-tight">$0</h2>
        <p class="text-xs text-slate-500 mt-4 italic">Cálculo mensual pendiente</p>
      </div>
    </div>

    <!-- Recent Movements -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden">
      <div class="p-6 border-b border-slate-800 flex justify-between items-center">
        <h3 class="text-lg font-semibold text-white">Últimos Movimientos</h3>
        <router-link to="/movimientos" class="text-primary-500 hover:text-primary-400 text-sm font-medium">
          Ver todos
        </router-link>
      </div>
      
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th class="px-6 py-3 font-medium">Fecha</th>
              <th class="px-6 py-3 font-medium">Descripción</th>
              <th class="px-6 py-3 font-medium text-right">Monto</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <tr v-for="mov in movimientos.slice(0, 5)" :key="mov.id" class="hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4 text-sm text-slate-300">{{ mov.fecha }}</td>
              <td class="px-6 py-4 text-sm text-white font-medium">{{ mov.descripcion }}</td>
              <td class="px-6 py-4 text-sm text-right font-bold" :class="mov.tipo === 'ingreso' ? 'text-green-400' : 'text-red-400'">
                {{ mov.tipo === 'ingreso' ? '+' : '-' }}{{ formatCurrency(mov.monto) }}
              </td>
            </tr>
            <tr v-if="movimientos.length === 0" class="text-center">
              <td colspan="3" class="px-6 py-12 text-slate-500">No hay movimientos registrados</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
