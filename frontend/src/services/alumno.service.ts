import api from './api';

export const alumnoService = {
  async getAlumnos(params: any = {}) {
    const { data } = await api.get('/alumnos/', { params });
    return data;
  },

  async getAlumno(id: string) {
    const { data } = await api.get(`/alumnos/${id}`);
    return data;
  },

  async crearAlumno(alumnoData: any) {
    const { data } = await api.post('/alumnos/', alumnoData);
    return data;
  },

  async actualizarAlumno(id: string, alumnoData: any) {
    const { data } = await api.patch(`/alumnos/${id}`, alumnoData);
    return data;
  },

  async importarCSV(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post('/alumnos/importar-csv', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return data;
  }
};
