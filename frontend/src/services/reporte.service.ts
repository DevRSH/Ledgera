import api from './api';

export const reporteService = {
  async generarReporte(tipo: string, parametros: any) {
    const { data } = await api.post('/reportes/generar', { tipo, parametros });
    return data;
  },

  async getJobStatus(jobId: string) {
    const { data } = await api.get(`/reportes/jobs/${jobId}`);
    return data;
  },

  async descargarReporte(jobId: string) {
    // Para descargas, a menudo es mejor obtener la URL firmada o el blob
    const response = await api.get(`/reportes/jobs/${jobId}/descargar`, {
      responseType: 'blob',
    });
    return response.data;
  }
};

export const comunicacionService = {
  async enviarEstadoCuenta(alumnoId: string) {
    const { data } = await api.post('/comunicaciones/enviar-estado-cuenta', { alumno_id: alumnoId });
    return data;
  },

  async getHistorial(params: any = {}) {
    const { data } = await api.get('/comunicaciones/historial', { params });
    return data;
  }
};
