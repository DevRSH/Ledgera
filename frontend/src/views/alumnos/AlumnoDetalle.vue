<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { alumnoService } from '../../services/alumno.service';
import { cuotaService } from '../../services/cuota.service';
import EstadoBadge from '../../components/shared/EstadoBadge.vue';
import MontoDisplay from '../../components/shared/MontoDisplay.vue';
import FolioTag from '../../components/shared/FolioTag.vue';
import RegistrarPago from '../cuotas/RegistrarPago.vue';

const props = defineProps<{
  id: string;
}>();

const loading = ref(true);
const alumno = ref<any>(null);
const estadoDeuda = ref<any>(null);
const activeTab = ref('datos');
const showPagoModal = ref(false);
const selectedMes = ref<number | null>(null);

const fetchDatos = async () => {
  loading.value = true;
  try {
    const [alumnoData, deudaData] = await Promise.all([
      alumnoService.getAlumno(props.id),
      cuotaService.getEstadosDeuda(props.id, new Date().getFullYear())
    ]);
    alumno.value = alumnoData;
    estadoDeuda.value = deudaData;
  } finally {
    loading.value = false;
  }
};

onMounted(fetchDatos);

const meses = [
  'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
];

const openPago = (mesIdx: number) => {
  selectedMes.value = mesIdx + 3; // Marzo es 3
  showPagoModal.value = true;
};
</script>

<template>
  <div v-if="alumno" class="max-w-6xl mx-auto p-6">
    <!-- Header -->
    <div class="flex items-start justify-between mb-8">
      <div>
        <h1 class="text-3xl font-bold text-slate-800">
          {{ alumno.nombre }} {{ alumno.apellido_paterno }} {{ alumno.apellido_materno }}
        </h1>
        <p class="text-slate-500 font-mono mt-1">{{ alumno.rut }}</p>
      </div>
      <div class="text-right">
        <EstadoBadge v-if="estadoDeuda" :estado="estadoDeuda.estado" class="mb-2" />
        <div class="text-2xl font-bold text-slate-700">
          <MontoDisplay v-if="estadoDeuda" :monto="estadoDeuda.monto_adeudado" />
        </div>
        <p class="text-xs text-slate-400 uppercase tracking-wider font-semibold">Deuda Total</p>
      </div>
    </div>

    <!-- Tabs -->
    <div class="flex border-b border-slate-200 mb-6">
      <button 
        v-for="tab in ['datos', 'cuotas', 'historial']" 
        :key="tab"
        @click="activeTab = tab"
        class="px-6 py-3 font-medium capitalize transition-all border-b-2"
        :class="activeTab === tab ? 'border-emerald-600 text-emerald-600' : 'border-transparent text-slate-500 hover:text-slate-700'"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
      <!-- Datos -->
      <div v-if="activeTab === 'datos'" class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Información Personal</h3>
          <dl class="space-y-4">
            <div>
              <dt class="text-xs text-slate-400">Fecha de Nacimiento</dt>
              <dd class="text-slate-700">{{ alumno.fecha_nacimiento || 'No registrada' }}</dd>
            </div>
            <div>
              <dt class="text-xs text-slate-400">Observaciones</dt>
              <dd class="text-slate-700 text-sm">{{ alumno.observaciones || 'Sin observaciones' }}</dd>
            </div>
          </dl>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">Apoderado Titular</h3>
          <div v-if="alumno.apoderado_titular" class="bg-slate-50 p-4 rounded-lg">
            <p class="font-bold text-slate-700">{{ alumno.apoderado_titular.nombre }} {{ alumno.apoderado_titular.apellido_paterno }}</p>
            <p class="text-sm text-slate-600 mt-1 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              </svg>
              {{ alumno.apoderado_titular.email }}
            </p>
            <p class="text-sm text-slate-600 mt-1 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
              </svg>
              {{ alumno.apoderado_titular.telefono }}
            </p>
          </div>
        </div>
      </div>

      <!-- Cuotas -->
      <div v-if="activeTab === 'cuotas'">
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <div 
            v-for="(mes, idx) in meses" 
            :key="mes"
            @click="openPago(idx)"
            class="p-4 rounded-xl border-2 transition-all cursor-pointer hover:shadow-md"
            :class="[
              idx + 3 <= new Date().getMonth() + 1 ? 'border-red-100 bg-red-50' : 'border-slate-100 bg-white'
            ]"
          >
            <p class="text-xs font-bold text-slate-400 uppercase mb-2">{{ mes }}</p>
            <div class="flex items-center justify-between">
              <span class="text-sm font-semibold text-slate-700">Deuda</span>
              <span class="text-red-500">❌</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modales -->
    <RegistrarPago 
      v-if="showPagoModal" 
      :show="showPagoModal"
      :alumno-id="id"
      :mes-inicial="selectedMes"
      @close="showPagoModal = false"
      @created="fetchDatos"
    />
  </div>
</template>
