import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { cuotaService } from '../services/cuota.service';
import type { EstadoDeuda } from '../types/api.types';

export const useCuotaStore = defineStore('cuota', () => {
  const deudores = ref<EstadoDeuda[]>([]);
  const configCuotas = ref<any[]>([]);
  const loading = ref(false);
  const totalDeudaGeneral = ref(0);

  const cantidadDeudores = computed(() => deudores.value.length);

  async function fetchDeudores(año: number) {
    loading.value = true;
    try {
      const response = await cuotaService.getDeudores(año);
      deudores.value = response.data;
      totalDeudaGeneral.value = response.total_deuda;
    } finally {
      loading.value = false;
    }
  }

  async function fetchConfigCuotas(año: number) {
    try {
      configCuotas.value = await cuotaService.getConfigCuotas(año);
    } catch (err) {}
  }

  async function registrarPago(data: any) {
    loading.value = true;
    try {
      const res = await cuotaService.registrarPago(data);
      return res;
    } finally {
      loading.value = false;
    }
  }

  async function condonarCuota(data: any) {
    loading.value = true;
    try {
      await cuotaService.condonar(data);
    } finally {
      loading.value = false;
    }
  }

  return {
    deudores,
    configCuotas,
    loading,
    totalDeudaGeneral,
    cantidadDeudores,
    fetchDeudores,
    fetchConfigCuotas,
    registrarPago,
    condonarCuota
  };
});
