import api from './api';

export const movimientoService = {
  async getMovimientos(params: any) {
    const { data } = await api.get('/movimientos', { params });
    return data;
  },

  async getSaldoActual() {
    const { data } = await api.get('/movimientos/saldo');
    return data;
  },

  async getResumenMensual(año: number) {
    const { data } = await api.get('/movimientos/resumen-anual', { params: { año } });
    return data;
  },

  async crearMovimiento(movData: any) {
    const { data } = await api.post('/movimientos', movData);
    return data;
  },

  async anularMovimiento(id: string, motivo: string) {
    const { data } = await api.post(`/movimientos/${id}/anular`, { motivo });
    return data;
  },

  async getCategorias() {
    const { data } = await api.get('/movimientos/categorias');
    return data;
  }
};
