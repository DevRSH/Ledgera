<script setup lang="ts">
import { computed } from 'vue';

const props = withDefaults(defineProps<{
  monto: number;
  mostrar_signo?: boolean;
}>(), {
  mostrar_signo: false
});

const formattedMonto = computed(() => {
  return new Intl.NumberFormat('es-CL', {
    style: 'currency',
    currency: 'CLP',
  }).format(props.monto);
});

const sign = computed(() => {
  if (!props.mostrar_signo) return '';
  return props.monto > 0 ? '+' : '';
});

const colorClass = computed(() => {
  if (!props.mostrar_signo) return 'text-slate-900';
  if (props.monto > 0) return 'text-green-600 font-semibold';
  if (props.monto < 0) return 'text-red-600 font-semibold';
  return 'text-slate-500';
});
</script>

<template>
  <span :class="colorClass">
    {{ sign }}{{ formattedMonto }}
  </span>
</template>
