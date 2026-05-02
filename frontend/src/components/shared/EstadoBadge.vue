<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  estado: "al_dia" | "debe_1_2" | "debe_3_mas" | "condonado_total";
}>();

const config = computed(() => {
  switch (props.estado) {
    case 'al_dia':
      return { class: 'bg-green-100 text-green-800', label: 'Al día' };
    case 'debe_1_2':
      return { class: 'bg-amber-100 text-amber-800', label: 'Debe 1-2 meses' };
    case 'debe_3_mas':
      return { class: 'bg-red-100 text-red-800', label: 'Debe 3+ meses' };
    case 'condonado_total':
      return { class: 'bg-slate-100 text-slate-600', label: 'Condonado' };
    default:
      return { class: 'bg-gray-100 text-gray-600', label: 'Desconocido' };
  }
});
</script>

<template>
  <span 
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    :class="config.class"
  >
    {{ config.label }}
  </span>
</template>
