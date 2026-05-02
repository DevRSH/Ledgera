<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import api from '../../services/api';
import FolioTag from '../../components/shared/FolioTag.vue';
import MontoDisplay from '../../components/shared/MontoDisplay.vue';

const route = useRoute();
const folio = route.params.folio as string;

const loading = ref(true);
const comprobante = ref<any>(null);
const error = ref<string | null>(null);
const verificado = ref(false);

onMounted(async () => {
  try {
    // Usamos el endpoint público para permitir acceso sin login
    const { data } = await api.get(`/public/verify/${folio}`);
    if (data.valido) {
      comprobante.value = data;
      verificado.value = true;
    } else {
      error.value = data.motivo || 'Comprobante no válido';
    }
  } catch (err) {
    error.value = 'Error al verificar el comprobante';
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 flex items-center justify-center p-6">
    <div v-if="loading" class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto"></div>
      <p class="mt-4 text-slate-500 font-medium">Verificando autenticidad...</p>
    </div>

    <div v-else-if="error" class="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full text-center border-t-4 border-red-500">
      <div class="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </div>
      <h2 class="text-xl font-bold text-slate-800 mb-2">Comprobante Inválido</h2>
      <p class="text-slate-500 mb-6">{{ error }}</p>
      <router-link to="/login" class="text-emerald-600 font-bold hover:underline">Ir al Portal Interno</router-link>
    </div>

    <div v-else-if="comprobante" class="bg-white p-8 rounded-2xl shadow-xl max-w-md w-full border-t-4 border-emerald-500">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-xl font-bold text-slate-800">Comprobante Oficial</h2>
          <p class="text-slate-400 text-sm">Ledgera - Tesorería Escolar</p>
        </div>
        <div class="bg-emerald-50 text-emerald-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
          ✓ Verificado
        </div>
      </div>

      <div class="space-y-6">
        <div class="flex justify-between border-b border-slate-100 pb-4">
          <span class="text-slate-400 text-sm">Folio</span>
          <FolioTag :folio="comprobante.folio" />
        </div>

        <div class="space-y-1">
          <span class="text-slate-400 text-xs font-bold uppercase tracking-widest">Concepto</span>
          <p class="text-slate-700 font-medium">{{ comprobante.concepto }}</p>
        </div>

        <div class="space-y-1">
          <span class="text-slate-400 text-xs font-bold uppercase tracking-widest">Monto Pagado</span>
          <p class="text-2xl font-bold text-slate-800">
            <MontoDisplay :monto="comprobante.monto" />
          </p>
        </div>

        <div class="flex justify-between pt-4 border-t border-slate-100">
          <div>
            <span class="text-slate-400 text-xs font-bold uppercase">Fecha de Pago</span>
            <p class="text-sm text-slate-700 font-medium">{{ comprobante.fecha_pago }}</p>
          </div>
          <div class="text-right">
            <span class="text-slate-400 text-xs font-bold uppercase">Sistema</span>
            <p class="text-sm text-emerald-600 font-bold">Ledgera v1.0</p>
          </div>
        </div>
      </div>

      <div class="mt-8 pt-6 border-t-2 border-dashed border-slate-100">
        <p class="text-[10px] text-slate-400 text-center leading-tight">
          Este documento es una representación digital de una transacción interna. 
          Su validez legal está sujeta a los registros oficiales de la institución.
        </p>
      </div>
    </div>
  </div>
</template>
