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
      <div class="bg-slate-900/40 backdrop-blur-md border border-white/10 hover:border-primary-500/50 hover:bg-slate-800/40 transition-all duration-300 p-6 rounded-2xl shadow-xl hover:shadow-primary-500/10 hover:-translate-y-1">
        <div class="flex justify-between items-start mb-4">
          <p class="text-slate-400 text-sm font-medium uppercase tracking-wider">Saldo Disponible</p>
          <div class="p-2 bg-primary-500/10 rounded-lg text-primary-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          </div>
        </div>
        <h2 class="text-4xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r" :class="saldo >= 0 ? 'from-green-400 to-emerald-300' : 'from-red-400 to-rose-300'">
          {{ formatCurrency(saldo) }}
        </h2>
      </div>

      <div class="bg-slate-900/40 backdrop-blur-md border border-white/10 hover:border-white/20 transition-all duration-300 p-6 rounded-2xl shadow-xl">
        <div class="flex justify-between items-start mb-4">
          <p class="text-slate-400 text-sm font-medium uppercase tracking-wider">Ingresos del Mes</p>
          <div class="p-2 bg-emerald-500/10 rounded-lg text-emerald-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path></svg>
          </div>
        </div>
        <h2 class="text-3xl font-bold text-white tracking-tight">$0</h2>
      </div>

      <div class="bg-slate-900/40 backdrop-blur-md border border-white/10 hover:border-white/20 transition-all duration-300 p-6 rounded-2xl shadow-xl">
        <div class="flex justify-between items-start mb-4">
          <p class="text-slate-400 text-sm font-medium uppercase tracking-wider">Egresos del Mes</p>
          <div class="p-2 bg-rose-500/10 rounded-lg text-rose-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path></svg>
          </div>
        </div>
        <h2 class="text-3xl font-bold text-white tracking-tight">$0</h2>
      </div>
    </div>

    <!-- Recent Movements -->
    <div class="bg-slate-900/40 backdrop-blur-md border border-white/10 rounded-2xl shadow-xl overflow-hidden mt-8 transition-all hover:border-primary-500/30">
      <div class="p-6 border-b border-white/10 flex justify-between items-center">
        <h3 class="text-lg font-semibold text-white flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-primary-500 shadow-[0_0_8px_rgba(14,165,233,0.8)]"></span>
          Últimos Movimientos
        </h3>
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
          <tbody class="divide-y divide-white/5">
            <tr v-for="mov in movimientos.slice(0, 5)" :key="mov.id" class="hover:bg-white/5 transition-colors group">
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
