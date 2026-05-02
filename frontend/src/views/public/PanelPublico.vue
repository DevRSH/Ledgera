<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import MontoDisplay from '../../components/shared/MontoDisplay.vue';

const loading = ref(true);
const saldo = ref(0);
const movimientos = ref<any[]>([]);
const actualizadoAt = ref(new Date().toLocaleString());

const tenantId = '00000000-0000-0000-0000-000000000000'; // Mock o inyectado desde dominio

onMounted(async () => {
  try {
    // En una app multi-tenant real, el ID vendría de la URL o subdominio
    // Aquí usamos una llamada genérica al endpoint público
    const [saldoRes, movsRes] = await Promise.all([
      api.get(`/public/${tenantId}/saldo`),
      api.get(`/public/${tenantId}/movimientos`)
    ]);
    saldo.value = saldoRes.data.saldo;
    movimientos.value = movsRes.data;
  } catch (err) {
    console.error('Error al cargar panel público');
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 p-6 md:p-12">
    <div class="max-w-5xl mx-auto">
      
      <!-- Public Header -->
      <header class="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 gap-6">
        <div>
          <div class="flex items-center space-x-2 mb-2">
            <span class="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></span>
            <span class="text-xs font-bold text-slate-400 uppercase tracking-widest">Portal de Transparencia</span>
          </div>
          <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight">Ledgera <span class="text-emerald-600">Público</span></h1>
          <p class="text-slate-500 mt-2 max-w-md">Información financiera actualizada en tiempo real para la comunidad escolar.</p>
        </div>
        
        <div class="bg-white p-6 rounded-3xl shadow-xl shadow-slate-200 border border-slate-100 text-right min-w-[240px]">
          <p class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Saldo Disponible</p>
          <div class="text-4xl font-black text-slate-900">
            <MontoDisplay :monto="saldo" />
          </div>
          <p class="text-[10px] text-slate-300 mt-2 uppercase font-bold">Corte: {{ actualizadoAt }}</p>
        </div>
      </header>

      <!-- Main Content -->
      <div class="grid grid-cols-1 gap-8">
        
        <!-- Movements Table (Sanitized) -->
        <section class="bg-white rounded-3xl shadow-sm border border-slate-100 overflow-hidden">
          <div class="p-6 border-b border-slate-50 flex justify-between items-center">
            <h2 class="font-bold text-slate-800">Últimos Movimientos</h2>
            <span class="text-xs font-semibold text-slate-400 bg-slate-50 px-2 py-1 rounded">Muestra: 20 registros</span>
          </div>
          
          <div class="overflow-x-auto">
            <table class="w-full text-left">
              <thead>
                <tr class="bg-slate-50">
                  <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Fecha</th>
                  <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Descripción</th>
                  <th class="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Monto</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-slate-50">
                <tr v-for="mov in movimientos" :key="mov.id" class="hover:bg-slate-50/50 transition-colors">
                  <td class="px-6 py-4 text-sm text-slate-500 font-medium">{{ mov.fecha }}</td>
                  <td class="px-6 py-4">
                    <p class="text-sm font-bold text-slate-700">{{ mov.descripcion }}</p>
                    <span class="text-[9px] font-black uppercase text-slate-300">{{ mov.tipo }}</span>
                  </td>
                  <td class="px-6 py-4 text-right">
                    <MontoDisplay :monto="mov.tipo === 'egreso' ? -mov.monto : mov.monto" :mostrar_signo="true" />
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <div v-if="movimientos.length === 0" class="p-12 text-center">
            <p class="text-slate-400 italic">No hay movimientos recientes registrados.</p>
          </div>
        </section>

      </div>

      <!-- Footer -->
      <footer class="mt-12 text-center">
        <p class="text-xs text-slate-400">Ledgera v1.0 — Chile. Potenciado por Transparencia Escolar.</p>
        <div class="mt-4 space-x-4">
          <router-link to="/login" class="text-xs font-bold text-emerald-600 hover:text-emerald-700">Acceso Tesorería</router-link>
          <span class="text-slate-200">|</span>
          <a href="#" class="text-xs font-bold text-slate-400 hover:text-slate-600">Manual de Usuario</a>
        </div>
      </footer>

    </div>
  </div>
</template>
