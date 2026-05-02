<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue';

const props = withDefaults(defineProps<{
  show: boolean;
  titulo: string;
  mensaje: string;
  tipo?: "danger" | "warning" | "info";
  confirmLabel?: string;
  cancelLabel?: string;
}>(), {
  tipo: 'info',
  confirmLabel: 'Confirmar',
  cancelLabel: 'Cancelar'
});

const emit = defineEmits<{
  (e: 'confirm'): void;
  (e: 'cancel'): void;
}>();

const handleEscape = (e: KeyboardEvent) => {
  if (e.key === 'Escape' && props.show) {
    emit('cancel');
  }
};

onMounted(() => window.addEventListener('keydown', handleEscape));
onUnmounted(() => window.removeEventListener('keydown', handleEscape));

const typeConfig = {
  danger: {
    btn: 'bg-red-600 hover:bg-red-700 focus:ring-red-500',
    icon: 'text-red-600',
    bgIcon: 'bg-red-100'
  },
  warning: {
    btn: 'bg-amber-500 hover:bg-amber-600 focus:ring-amber-400',
    icon: 'text-amber-600',
    bgIcon: 'bg-amber-100'
  },
  info: {
    btn: 'bg-emerald-600 hover:bg-emerald-700 focus:ring-emerald-500',
    icon: 'text-emerald-600',
    bgIcon: 'bg-emerald-100'
  }
};
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="ease-out duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="show" class="fixed inset-0 bg-slate-900 bg-opacity-50 transition-opacity z-50 flex items-center justify-center p-4">
        <div 
          class="bg-white rounded-lg shadow-xl transform transition-all sm:max-w-lg sm:w-full overflow-hidden"
          @click.stop
        >
          <div class="px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div class="sm:flex sm:items-start">
              <div 
                class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10"
                :class="typeConfig[tipo].bgIcon"
              >
                <!-- Icon based on type -->
                <svg v-if="tipo === 'danger' || tipo === 'warning'" class="h-6 w-6" :class="typeConfig[tipo].icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <svg v-else class="h-6 w-6" :class="typeConfig[tipo].icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                <h3 class="text-lg leading-6 font-medium text-slate-900">{{ titulo }}</h3>
                <div class="mt-2">
                  <p class="text-sm text-slate-500">{{ mensaje }}</p>
                </div>
              </div>
            </div>
          </div>
          <div class="bg-slate-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button 
              @click="emit('confirm')"
              type="button" 
              class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm"
              :class="typeConfig[tipo].btn"
            >
              {{ confirmLabel }}
            </button>
            <button 
              @click="emit('cancel')"
              type="button" 
              class="mt-3 w-full inline-flex justify-center rounded-md border border-slate-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-slate-700 hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-emerald-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            >
              {{ cancelLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
