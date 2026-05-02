import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { movimientoService } from '../services/movimiento.service';
import type { Movimiento } from '../types/api.types';

export const useMovimientoStore = defineStore('movimiento', () => {
  const movimientos = ref<Movimiento[]>([]);
  const saldoActual = ref(0);
  const resumenMensual = ref<any[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const totalIngresosMes = computed(() => {
    return movimientos.value
      .filter(m => m.tipo === 'ingreso' && !m.anulado)
      .reduce((acc, curr) => acc + curr.monto, 0);
  });

  const totalEgresosMes = computed(() => {
    return movimientos.value
      .filter(m => m.tipo === 'egreso' && !m.anulado)
      .reduce((acc, curr) => acc + curr.monto, 0);
  });

  async function fetchMovimientos(filtros: any = {}) {
    loading.value = true;
    error.value = null;
    try {
      const response = await movimientoService.getMovimientos(filtros);
      movimientos.value = response.data;
    } catch (err: any) {
      error.value = err.message || 'Error al cargar movimientos';
    } finally {
      loading.value = false;
    }
  }

  async function fetchSaldoActual() {
    try {
      const response = await movimientoService.getSaldoActual();
      saldoActual.value = response.saldo;
    } catch (err) {}
  }

  async function fetchResumenMensual(año: number) {
    try {
      resumenMensual.value = await movimientoService.getResumenMensual(año);
    } catch (err) {}
  }

  async function crearMovimiento(data: any) {
    loading.value = true;
    try {
      await movimientoService.crearMovimiento(data);
      await fetchMovimientos();
      await fetchSaldoActual();
    } finally {
      loading.value = false;
    }
  }

  async function anularMovimiento(id: string, motivo: string) {
    loading.value = true;
    try {
      await movimientoService.anularMovimiento(id, motivo);
      await fetchMovimientos();
      await fetchSaldoActual();
    } finally {
      loading.value = false;
    }
  }

  return {
    movimientos,
    saldoActual,
    resumenMensual,
    loading,
    error,
    totalIngresosMes,
    totalEgresosMes,
    fetchMovimientos,
    fetchSaldoActual,
    fetchResumenMensual,
    crearMovimiento,
    anularMovimiento
  };
});
