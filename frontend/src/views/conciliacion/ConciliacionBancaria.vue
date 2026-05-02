<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import MontoDisplay from '../../components/shared/MontoDisplay.vue';
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue';
import { useAuthStore } from '../../stores/auth.store';

const authStore = useAuthStore();
const periodos = ref<any[]>([]);
const selectedPeriodo = ref<any>(null);
const lineasBancarias = ref<any[]>([]);
const movimientosCandidatos = ref<any[]>([]);
const showCerrarDialog = ref(false);

onMounted(async () => {
  const { data } = await api.get('/conciliacion');
  periodos.value = data.data;
});

const selectPeriodo = async (p: any) => {
  selectedPeriodo.value = p;
  const [lineasRes, movsRes] = await Promise.all([
    api.get(`/conciliacion/${p.id}/diferencias`),
    api.get('/movimientos', { params: { conciliado: false } })
  ]);
  lineasBancarias.value = lineasRes.data;
  movimientosCandidatos.value = movsRes.data.data;
};

const autoConciliar = async () => {
  if (!selectedPeriodo.value) return;
  const { data } = await api.post(`/conciliacion/${selectedPeriodo.value.id}/auto-conciliar`);
  alert(`Proceso terminado: ${data.conciliados} movimientos conciliados.`);
  await selectPeriodo(selectedPeriodo.value);
};

const cerrarPeriodo = async () => {
  await api.post(`/conciliacion/${selectedPeriodo.value.id}/cerrar`);
  showCerrarDialog.value = false;
  // Refresh list
};
</script>

<template>
  <div class="p-6 max-w-[1600px] mx-auto h-[calc(100vh-100px)] flex flex-col">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Conciliación Bancaria</h1>
        <p class="text-sm text-slate-500">Cruce de información entre banco y contabilidad interna</p>
      </div>
      <div v-if="selectedPeriodo" class="flex items-center space-x-3">
        <button 
          @click="autoConciliar"
          class="px-4 py-2 bg-emerald-100 text-emerald-700 rounded-lg font-bold text-sm hover:bg-emerald-200 transition-colors"
        >
          Auto-conciliar
        </button>
        <button 
          v-if="authStore.user?.rol === 'DIRECTIVA' || authStore.user?.rol === 'SUPER_ADMIN'"
          @click="showCerrarDialog = true"
          class="px-4 py-2 bg-slate-800 text-white rounded-lg font-bold text-sm hover:bg-slate-900 transition-colors"
        >
          Cerrar Período
        </button>
      </div>
    </div>

    <div class="flex flex-1 gap-6 overflow-hidden">
      <!-- Master: Periodos -->
      <aside class="w-64 bg-white rounded-2xl shadow-sm border border-slate-100 overflow-y-auto">
        <div class="p-4 border-b border-slate-50 font-bold text-xs text-slate-400 uppercase tracking-widest">Períodos</div>
        <div class="divide-y divide-slate-50">
          <button 
            v-for="p in periodos" 
            :key="p.id"
            @click="selectPeriodo(p)"
            class="w-full text-left p-4 hover:bg-slate-50 transition-colors"
            :class="selectedPeriodo?.id === p.id ? 'bg-emerald-50 border-r-4 border-emerald-500' : ''"
          >
            <p class="font-bold text-slate-700 capitalize">{{ p.mes }} {{ p.año }}</p>
            <span class="text-[10px] font-bold px-2 py-0.5 rounded uppercase" :class="p.estado === 'conciliada' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'">
              {{ p.estado }}
            </span>
          </button>
        </div>
      </aside>

      <!-- Detail: Comparison -->
      <main v-if="selectedPeriodo" class="flex-1 flex gap-6 overflow-hidden">
        <!-- Banco -->
        <div class="flex-1 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col overflow-hidden">
          <div class="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
            <h3 class="font-bold text-slate-700 text-sm">Líneas del Banco</h3>
            <span class="text-xs text-slate-400">{{ lineasBancarias.length }} pendientes</span>
          </div>
          <div class="flex-1 overflow-y-auto p-2 space-y-2">
            <div 
              v-for="linea in lineasBancarias" 
              :key="linea.id"
              class="p-3 border border-slate-100 rounded-xl hover:border-emerald-300 transition-all cursor-pointer group"
            >
              <div class="flex justify-between items-start">
                <span class="text-[10px] font-bold text-slate-400">{{ linea.fecha }}</span>
                <MontoDisplay :monto="linea.monto" class="text-sm font-black" />
              </div>
              <p class="text-xs text-slate-600 mt-1 line-clamp-1">{{ linea.descripcion }}</p>
            </div>
          </div>
        </div>

        <!-- Sistema -->
        <div class="flex-1 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col overflow-hidden">
          <div class="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
            <h3 class="font-bold text-slate-700 text-sm">Movimientos Ledgera</h3>
            <span class="text-xs text-slate-400">{{ movimientosCandidatos.length }} sin conciliar</span>
          </div>
          <div class="flex-1 overflow-y-auto p-2 space-y-2">
            <div 
              v-for="mov in movimientosCandidatos" 
              :key="mov.id"
              class="p-3 border border-slate-100 rounded-xl hover:border-emerald-300 transition-all"
            >
              <div class="flex justify-between items-start">
                <span class="text-[10px] font-bold text-slate-400">{{ mov.fecha }}</span>
                <MontoDisplay :monto="mov.tipo === 'egreso' ? -mov.monto : mov.monto" class="text-sm font-black" />
              </div>
              <p class="text-xs text-slate-600 mt-1">{{ mov.descripcion }}</p>
            </div>
          </div>
        </div>
      </main>

      <div v-else class="flex-1 bg-white rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center justify-center text-slate-400 italic">
        Selecciona un período para iniciar la conciliación
      </div>
    </div>

    <ConfirmDialog 
      :show="showCerrarDialog"
      titulo="¿Cerrar Período de Conciliación?"
      mensaje="Al cerrar el período, no se podrán realizar más cruces. El estado se actualizará basándose en las diferencias remanentes."
      tipo="warning"
      @cancel="showCerrarDialog = false"
      @confirm="cerrarPeriodo"
    />
  </div>
</template>
