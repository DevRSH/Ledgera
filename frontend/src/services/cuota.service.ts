import api from './api';

export const cuotaService = {
  async getEstadosDeuda(alumnoId: string, año: number) {
    const { data } = await api.get(`/cuotas/estado/${alumnoId}`, { params: { año } });
    return data;
  },

  async getDeudores(año: number) {
    const { data } = await api.get('/cuotas/deudores', { params: { año } });
    return data;
  },

  async registrarPago(pagoData: any) {
    const { data } = await api.post('/cuotas/pago', pagoData);
    return data;
  },

  async getConfigCuotas(año: number) {
    const { data } = await api.get('/cuotas/config', { params: { año } });
    return data;
  },

  async setConfigCuotas(configs: any[]) {
    const { data } = await api.post('/cuotas/config', configs);
    return data;
  },

  async condonar(condonacionData: any) {
    const { data } = await api.post('/cuotas/condonacion', condonacionData);
    return data;
  }
};
