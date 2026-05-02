<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { cuotaService } from '../../services/cuota.service';
import { alumnoService } from '../../services/alumno.service';
import FolioTag from '../../components/shared/FolioTag.vue';

const props = defineProps<{
  show: boolean;
  alumnoId?: string;
  mesInicial?: number;
}>();

const emit = defineEmits(['close', 'created']);

const loading = ref(false);
const step = ref(1); // 1: Form, 2: Success
const generatedFolio = ref('');
const alumnos = ref<any[]>([]);

const form = ref({
  alumno_id: props.alumnoId || '',
  mes: props.mesInicial || new Date().getMonth() + 1,
  año: new Date().getFullYear(),
  monto: 15000,
  forma_pago: 'efectivo'
});

onMounted(async () => {
  if (!props.alumnoId) {
    const data = await alumnoService.getAlumnos();
    alumnos.value = data.data;
  }
});

const submit = async () => {
  loading.value = true;
  try {
    const res = await cuotaService.registrarPago(form.value);
    generatedFolio.value = res.folio;
    // resultPdfUrl.value = res.pdf_url;
    step.value = 2;
    emit('created');
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Teleport to="body">
    <div v-if="show" class="fixed inset-0 bg-slate-900 bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden">
        
        <!-- Step 1: Form -->
        <div v-if="step === 1">
          <div class="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
            <h3 class="font-bold text-slate-700">Registrar Pago de Cuota</h3>
            <button @click="emit('close')" class="text-slate-400 hover:text-slate-600">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <form @submit.prevent="submit" class="p-6 space-y-6">
            <div v-if="!alumnoId">
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Alumno</label>
              <select v-model="form.alumno_id" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm" required>
                <option value="">Seleccionar alumno...</option>
                <option v-for="a in alumnos" :key="a.id" :value="a.id">{{ a.nombre }} {{ a.apellido_paterno }}</option>
              </select>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Mes</label>
                <select v-model="form.mes" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
                  <option v-for="m in 12" :key="m" :value="m">{{ m }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Monto</label>
                <input v-model.number="form.monto" type="number" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm font-bold" />
              </div>
            </div>

            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Forma de Pago</label>
              <div class="grid grid-cols-2 gap-2">
                <button 
                  type="button" 
                  v-for="fp in ['efectivo', 'transferencia']" 
                  :key="fp"
                  @click="form.forma_pago = fp"
                  class="py-2 border-2 rounded-lg text-sm font-semibold capitalize"
                  :class="form.forma_pago === fp ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-slate-100 text-slate-500'"
                >
                  {{ fp }}
                </button>
              </div>
            </div>

            <button 
              type="submit" 
              :disabled="loading"
              class="w-full py-4 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl font-bold shadow-lg shadow-emerald-100 transition-all"
            >
              {{ loading ? 'Registrando...' : 'Confirmar Pago' }}
            </button>
          </form>
        </div>

        <!-- Step 2: Success -->
        <div v-else class="p-8 text-center">
          <div class="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-slate-800 mb-2">¡Pago Exitoso!</h3>
          <p class="text-slate-500 mb-6">El pago ha sido registrado correctamente en el sistema.</p>
          
          <div class="bg-slate-50 p-4 rounded-xl mb-8">
            <p class="text-xs font-bold text-slate-400 uppercase mb-2">Folio Comprobante</p>
            <FolioTag :folio="generatedFolio" />
          </div>

          <div class="space-y-3">
            <button class="w-full py-3 bg-slate-800 text-white rounded-xl font-bold flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Descargar PDF
            </button>
            <button 
              @click="emit('close')"
              class="w-full py-3 text-slate-500 font-semibold hover:text-slate-700"
            >
              Cerrar
            </button>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>
