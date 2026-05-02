<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useMovimientoStore } from '../../stores/movimiento.store';
import { storeToRefs } from 'pinia';
import MontoDisplay from '../../components/shared/MontoDisplay.vue';
import ConfirmDialog from '../../components/shared/ConfirmDialog.vue';
import MovimientoForm from './MovimientoForm.vue';
import { useAuthStore } from '../../stores/auth.store';

const movimientoStore = useMovimientoStore();
const { movimientos, saldoActual } = storeToRefs(movimientoStore);
const authStore = useAuthStore();

const showCreateModal = ref(false);
const showAnularDialog = ref(false);
const selectedMovId = ref<string | null>(null);

onMounted(() => {
  movimientoStore.fetchMovimientos();
  movimientoStore.fetchSaldoActual();
});

const handleAnular = (id: string) => {
  selectedMovId.value = id;
  showAnularDialog.value = true;
};

const confirmAnulacion = async () => {
  if (selectedMovId.value) {
    await movimientoStore.anularMovimiento(selectedMovId.value, 'Anulación administrativa');
    showAnularDialog.value = false;
  }
};
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto">
    <!-- Header & Stats -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
      <div>
        <h1 class="text-2xl font-bold text-slate-800">Movimientos de Caja</h1>
        <p class="text-slate-500">Gestión de ingresos y egresos de la tesorería</p>
      </div>
      
      <div class="flex items-center space-x-6 bg-white p-4 rounded-xl shadow-sm border border-slate-100">
        <div class="text-right">
          <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">Saldo Total</p>
          <div class="text-2xl font-bold text-emerald-600">
            <MontoDisplay :monto="saldoActual" />
          </div>
        </div>
        <button 
          v-if="authStore.user?.rol === 'TESORERO' || authStore.user?.rol === 'SUPER_ADMIN'"
          @click="showCreateModal = true"
          class="bg-emerald-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-emerald-700 shadow-lg shadow-emerald-100 transition-all flex items-center"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Nuevo Movimiento
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="bg-slate-50 border-b border-slate-100">
            <th class="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Fecha</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Tipo</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-400 uppercase">Descripción</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-400 uppercase text-right">Monto</th>
            <th class="px-6 py-4 text-xs font-bold text-slate-400 uppercase text-center">Acciones</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-slate-50">
          <tr 
            v-for="mov in movimientos" 
            :key="mov.id"
            class="hover:bg-slate-50 transition-colors"
            :class="{ 'opacity-50 grayscale italic': mov.anulado }"
          >
            <td class="px-6 py-4 text-sm text-slate-600">{{ mov.fecha }}</td>
            <td class="px-6 py-4">
              <span 
                class="px-2 py-1 rounded-md text-[10px] font-bold uppercase"
                :class="mov.tipo === 'ingreso' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'"
              >
                {{ mov.tipo }}
              </span>
              <span v-if="mov.anulado" class="ml-2 bg-slate-200 text-slate-600 px-2 py-0.5 rounded text-[10px] font-bold uppercase">Anulado</span>
            </td>
            <td class="px-6 py-4">
              <p class="text-sm font-medium text-slate-700">{{ mov.descripcion }}</p>
              <p v-if="mov.nombre_categoria" class="text-xs text-slate-400">{{ mov.nombre_categoria }}</p>
            </td>
            <td class="px-6 py-4 text-right">
              <MontoDisplay :monto="mov.tipo === 'egreso' ? -mov.monto : mov.monto" :mostrar_signo="true" />
            </td>
            <td class="px-6 py-4 text-center">
              <button 
                v-if="!mov.anulado && authStore.user?.rol === 'DIRECTIVA' || authStore.user?.rol === 'SUPER_ADMIN'"
                @click="handleAnular(mov.id)"
                class="text-red-400 hover:text-red-600 p-1 rounded hover:bg-red-50 transition-all"
                title="Anular movimiento"
              >
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modales -->
    <MovimientoForm v-if="showCreateModal" @close="showCreateModal = false" @created="movimientoStore.fetchMovimientos()" />
    
    <ConfirmDialog 
      :show="showAnularDialog"
      titulo="¿Anular Movimiento?"
      mensaje="Esta acción marcará el movimiento como anulado y revertirá su impacto en el saldo actual. Se registrará la anulación en el historial."
      tipo="danger"
      @cancel="showAnularDialog = false"
      @confirm="confirmAnulacion"
    />
  </div>
</template>
