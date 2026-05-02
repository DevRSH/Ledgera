<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  folio: string;
}>();

const copiado = ref(false);

const copiar = async () => {
  try {
    await navigator.clipboard.writeText(props.folio);
    copiado.value = true;
    setTimeout(() => {
      copiado.value = false;
    }, 2000);
  } catch (err) {
    console.error('Error al copiar:', err);
  }
};
</script>

<template>
  <div 
    class="inline-flex items-center space-x-2 bg-slate-100 border border-slate-200 px-2 py-1 rounded font-mono text-sm group"
  >
    <span class="text-slate-700">{{ folio }}</span>
    <button 
      @click="copiar"
      class="text-slate-400 hover:text-emerald-600 transition-colors p-0.5 rounded"
      :title="copiado ? '¡Copiado!' : 'Copiar folio'"
    >
      <svg v-if="!copiado" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2h-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2" />
      </svg>
      <span v-else class="text-[10px] font-bold text-emerald-600">¡COPIADO!</span>
    </button>
  </div>
</template>
