<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../services/api';

const alumnos = ref<any[]>([]);
const config = ref<any[]>([]);
const loading = ref(true);
const selectedYear = ref(new Date().getFullYear());

async function fetchData() {
  loading.value = true;
  try {
    const [alRes, confRes] = await Promise.all([
      api.get('/alumnos/'),
      api.get(`/cuotas/config?año=${selectedYear.value}`)
    ]);
    
    alumnos.value = alRes.data;
    config.value = confRes.data;
    
    // For each alumno, fetch their debt status
    // Note: In production, this should be a bulk endpoint
    for (const al of alumnos.value) {
      const statusRes = await api.get(`/cuotas/estado/${al.id}?año=${selectedYear.value}`);
      al.status = statusRes.data;
    }
  } catch (error) {
    console.error('Error fetching cuotas data:', error);
  } finally {
    loading.value = false;
  }
}

function getStatusIcon(alumno: any, mes: number) {
  if (!alumno.status) return '⬜';
  if (alumno.status.meses_pagados.includes(mes)) return '✅';
  if (alumno.status.meses_adeudados.includes(mes)) return '❌';
  return '⬜';
}

onMounted(fetchData);
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-white">Matriz de Cuotas</h1>
        <p class="text-slate-400">Control de pagos por alumno y mes</p>
      </div>
      <div class="flex gap-4 items-center">
        <select v-model="selectedYear" @change="fetchData" class="bg-slate-900 border border-slate-800 text-white rounded-lg px-3 py-1.5 text-sm">
          <option v-for="y in [2024, 2025, 2026]" :key="y" :value="y">{{ y }}</option>
        </select>
        <button class="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          Configurar Montos
        </button>
      </div>
    </header>

    <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-sm">
          <thead class="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th class="px-6 py-4 font-medium sticky left-0 bg-slate-950 z-10">Alumno</th>
              <th v-for="mes in 12" :key="mes" class="px-3 py-4 font-medium text-center">
                {{ ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'][mes-1] }}
              </th>
              <th class="px-6 py-4 font-medium text-right">Deuda Total</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <tr v-for="al in alumnos" :key="al.id" class="hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4 font-medium text-white sticky left-0 bg-slate-900 z-10 shadow-[2px_0_5px_rgba(0,0,0,0.3)]">
                {{ al.apellido_paterno }}, {{ al.nombre[0] }}.
              </td>
              <td v-for="mes in 12" :key="mes" class="px-3 py-4 text-center text-lg">
                {{ getStatusIcon(al, mes) }}
              </td>
              <td class="px-6 py-4 text-right font-bold" :class="al.status?.monto_adeudado > 0 ? 'text-red-400' : 'text-green-400'">
                {{ al.status ? new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(al.status.monto_adeudado) : '$0' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div class="p-4 bg-slate-950/50 border-t border-slate-800 flex gap-6 text-xs text-slate-400 justify-center">
        <div class="flex items-center"><span class="mr-2">✅</span> Pagado</div>
        <div class="flex items-center"><span class="mr-2">❌</span> Adeuda</div>
        <div class="flex items-center"><span class="mr-2">⬜</span> No aplica</div>
      </div>
    </div>
  </div>
</template>
