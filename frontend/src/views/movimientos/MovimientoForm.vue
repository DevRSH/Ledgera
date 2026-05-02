<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { movimientoService } from '../../services/movimiento.service';

const emit = defineEmits(['close', 'created']);

const loading = ref(false);
const formError = ref('');
const categorias = ref<any[]>([]);

const form = ref({
  tipo: 'ingreso',
  monto: 0,
  fecha: new Date().toISOString().split('T')[0],
  descripcion: '',
  categoria_id: '',
  forma_pago: 'transferencia'
});

onMounted(async () => {
  try {
    categorias.value = await movimientoService.getCategorias();
  } catch (err) {}
});

const submit = async () => {
  loading.value = true;
  formError.value = '';
  try {
    await movimientoService.crearMovimiento(form.value);
    emit('created');
    emit('close');
  } catch (err: any) {
    console.error(err);
    formError.value = err.response?.data?.detail || 'Error al registrar el movimiento.';
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 bg-slate-900 bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
        <div class="bg-slate-50 px-6 py-4 border-b border-slate-100 flex justify-between items-center">
          <h3 class="font-bold text-slate-700">Registrar Nuevo Movimiento</h3>
          <button @click="emit('close')" class="text-slate-400 hover:text-slate-600">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form @submit.prevent="submit" class="p-6 space-y-4">
          <div class="flex p-1 bg-slate-100 rounded-lg">
            <button 
              type="button" 
              @click="form.tipo = 'ingreso'"
              class="flex-1 py-2 rounded-md text-sm font-bold transition-all"
              :class="form.tipo === 'ingreso' ? 'bg-white text-emerald-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            >
              INGRESO
            </button>
            <button 
              type="button" 
              @click="form.tipo = 'egreso'"
              class="flex-1 py-2 rounded-md text-sm font-bold transition-all"
              :class="form.tipo === 'egreso' ? 'bg-white text-red-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
            >
              EGRESO
            </button>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Monto (CLP)</label>
            <input 
              v-model.number="form.monto" 
              type="number" 
              class="w-full text-2xl font-bold text-slate-700 border-b-2 border-slate-200 focus:border-emerald-500 outline-none py-1"
              required
            />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Fecha</label>
              <input v-model="form.fecha" type="date" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm" required />
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Categoría</label>
              <select v-model="form.categoria_id" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
                <option value="">Sin categoría</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.id">{{ cat.nombre }}</option>
              </select>
            </div>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-400 uppercase mb-1">Descripción</label>
            <textarea 
              v-model="form.descripcion" 
              rows="3" 
              class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm outline-none focus:ring-2 focus:ring-emerald-500/20"
              placeholder="Ej: Pago de materiales escolares..."
              required
            ></textarea>
          </div>

          <div v-if="formError" class="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded-lg text-sm">
            {{ formError }}
          </div>

          <button 
            type="submit" 
            :disabled="loading"
            class="w-full py-3 rounded-xl font-bold text-white transition-all shadow-lg"
            :class="form.tipo === 'ingreso' ? 'bg-emerald-600 hover:bg-emerald-700 shadow-emerald-100' : 'bg-red-600 hover:bg-red-700 shadow-red-100'"
          >
            {{ loading ? 'Procesando...' : 'Confirmar ' + form.tipo }}
          </button>
        </form>
      </div>
    </div>
  </Teleport>
</template>
