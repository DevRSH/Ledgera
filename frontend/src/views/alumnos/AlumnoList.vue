<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../../services/api';
import { alumnoService } from '../../services/alumno.service';

const alumnos = ref<any[]>([]);
const loading = ref(true);
const importMessage = ref('');
const importError = ref('');
const isImporting = ref(false);
const fileInput = ref<HTMLInputElement | null>(null);

async function fetchAlumnos() {
  loading.value = true;
  try {
    const response = await api.get('/alumnos/');
    alumnos.value = response.data.data || [];
  } catch (error) {
    console.error('Error fetching alumnos:', error);
  } finally {
    loading.value = false;
  }
}

async function handleFileUpload(event: Event) {
  const target = event.target as HTMLInputElement;
  if (!target.files || target.files.length === 0) return;
  
  const file = target.files[0];
  isImporting.value = true;
  importMessage.value = '';
  importError.value = '';
  
  try {
    const result = await alumnoService.importarCSV(file);
    importMessage.value = `Importación exitosa: ${result.importados} alumnos importados. ${result.errores.length > 0 ? result.errores.length + ' errores.' : ''}`;
    await fetchAlumnos();
  } catch (error: any) {
    console.error('Error importing CSV:', error);
    importError.value = error.response?.data?.detail || 'Error al importar el archivo CSV.';
  } finally {
    isImporting.value = false;
    if (fileInput.value) fileInput.value.value = ''; // Reset input
  }
}

function triggerFileInput() {
  fileInput.value?.click();
}

onMounted(fetchAlumnos);
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-white">Alumnos</h1>
        <p class="text-slate-400">Listado de alumnos y apoderados</p>
      </div>
      <div class="flex gap-3">
        <input type="file" ref="fileInput" @change="handleFileUpload" accept=".csv" class="hidden" />
        <button 
          @click="triggerFileInput"
          :disabled="isImporting"
          class="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
        >
          {{ isImporting ? 'Importando...' : 'Importar CSV' }}
        </button>
        <router-link to="/alumnos/nuevo" class="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors shadow-lg shadow-primary-600/20">
          Nuevo Alumno
        </router-link>
      </div>
    </header>

    <div v-if="importMessage" class="bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 px-4 py-3 rounded-lg text-sm">
      {{ importMessage }}
    </div>
    <div v-if="importError" class="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded-lg text-sm">
      {{ importError }}
    </div>

    <div class="bg-slate-900 border border-slate-800 rounded-2xl shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-950/50 text-slate-400 text-xs uppercase tracking-wider">
            <tr>
              <th class="px-6 py-3 font-medium">RUT</th>
              <th class="px-6 py-3 font-medium">Nombre Completo</th>
              <th class="px-6 py-3 font-medium text-center">Estado</th>
              <th class="px-6 py-3 font-medium text-right">Acciones</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800">
            <tr v-for="alumno in alumnos" :key="alumno.id" class="hover:bg-slate-800/30 transition-colors">
              <td class="px-6 py-4 text-sm font-mono text-slate-400">{{ alumno.rut }}</td>
              <td class="px-6 py-4 text-sm text-white font-medium">
                {{ alumno.nombre }} {{ alumno.apellido_paterno }} {{ alumno.apellido_materno }}
              </td>
              <td class="px-6 py-4 text-sm text-center">
                <span :class="alumno.activo ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'" class="px-2 py-0.5 rounded-full text-xs font-medium">
                  {{ alumno.activo ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-right">
                <router-link :to="`/alumnos/${alumno.id}`" class="text-primary-500 hover:text-primary-400 font-medium mr-3">Ver</router-link>
                <router-link :to="`/alumnos/${alumno.id}/editar`" class="text-slate-500 hover:text-white font-medium">Editar</router-link>
              </td>
            </tr>
            <tr v-if="alumnos.length === 0" class="text-center">
              <td colspan="4" class="px-6 py-12 text-slate-500">No hay alumnos registrados</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
