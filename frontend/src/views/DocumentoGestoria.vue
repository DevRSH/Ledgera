<script setup lang="ts">
import { ref, onMounted } from 'vue';
import api from '../services/api';

const documentos = ref<any[]>([]);
const loading = ref(true);

async function fetchDocumentos() {
  loading.value = true;
  try {
    const response = await api.get('/documentos/');
    documentos.value = response.data.data || [];
  } catch (error) {
    console.error('Error fetching documentos:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchDocumentos);
</script>

<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <header class="flex justify-between items-center">
      <div>
        <h1 class="text-3xl font-bold text-white">Gestión Documental</h1>
        <p class="text-slate-400">Repositorio de respaldos y comprobantes</p>
      </div>
      <button class="bg-primary-600 hover:bg-primary-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
        Subir Documento
      </button>
    </header>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="doc in documentos" :key="doc.id" class="bg-slate-900 border border-slate-800 rounded-xl p-4 hover:border-primary-500/50 transition-all group">
        <div class="flex items-start justify-between mb-4">
          <div class="p-3 bg-slate-950 rounded-lg text-primary-500">
            <span v-if="doc.tipo_documento === 'boleta'">🧾</span>
            <span v-else-if="doc.tipo_documento === 'foto'">📷</span>
            <span v-else>📄</span>
          </div>
          <a :href="doc.storage_url" target="_blank" class="text-xs text-slate-500 hover:text-primary-500 font-medium">
            Descargar
          </a>
        </div>
        
        <h3 class="text-white font-medium truncate mb-1" :title="doc.nombre_original">
          {{ doc.nombre_original }}
        </h3>
        <div class="flex items-center text-xs text-slate-500 uppercase tracking-tighter">
          <span class="bg-slate-800 px-1.5 py-0.5 rounded mr-2">{{ doc.tipo_documento }}</span>
        </div>
      </div>
      
      <div v-if="documentos.length === 0" class="col-span-full py-20 text-center bg-slate-900/30 border-2 border-dashed border-slate-800 rounded-2xl">
        <p class="text-slate-500">No hay documentos en el repositorio</p>
      </div>
    </div>
  </div>
</template>
