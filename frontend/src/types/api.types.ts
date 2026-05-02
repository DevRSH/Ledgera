export type Role = 'SUPER_ADMIN' | 'TESORERO' | 'DIRECTIVA' | 'AUDITOR' | 'APODERADO';

export interface Usuario {
  id: string;
  email: string;
  nombre: string;
  rol: Role;
  activo: boolean;
}

export interface Alumno {
  id: string;
  rut: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  fecha_nacimiento?: string;
  activo: boolean;
  apoderado_titular?: Apoderado;
  estado_deuda?: string;
  created_at: string;
}

export interface Apoderado {
  id: string;
  tipo: 'titular' | 'suplente';
  rut?: string;
  nombre: string;
  apellido_paterno: string;
  apellido_materno?: string;
  email?: string;
  telefono?: string;
  direccion?: string;
}

export interface Movimiento {
  id: string;
  tipo: 'ingreso' | 'egreso';
  monto: number;
  fecha: string;
  descripcion: string;
  categoria_id?: string;
  forma_pago: 'efectivo' | 'transferencia' | 'cheque' | 'otro';
  referencia_bancaria?: string;
  anulado: boolean;
  anulado_por?: string;
  motivo_anulacion?: string;
  nombre_categoria?: string;
  nombre_registrado_por?: string;
  created_at: string;
}

export interface EstadoDeuda {
  alumno_id: string;
  alumno_nombre: string;
  meses_configurados: number;
  meses_pagados: number;
  meses_condonados: number;
  meses_adeudados: number;
  monto_adeudado: number;
  estado: 'al_dia' | 'debe_1_2' | 'debe_3_mas' | 'condonado_total';
  ultimo_pago?: string;
}

export interface Comprobante {
  id: string;
  folio: string;
  alumno_nombre: string;
  mes: number;
  año: number;
  monto: number;
  fecha_pago: string;
  pdf_url?: string;
  anulado: boolean;
  created_at: string;
}

export interface Documento {
  id: string;
  nombre_original: string;
  mime_type: string;
  tamaño_bytes: number;
  tipo_documento: string;
  subido_por_nombre?: string;
  created_at: string;
}

export interface ReporteJob {
  id: string;
  tipo: string;
  estado: 'pendiente' | 'procesando' | 'completado' | 'error';
  created_at: string;
  resultado_url?: string;
  error_detalle?: string;
}

export interface EmailEnviado {
  id: string;
  alumno_nombre?: string;
  destinatario_email: string;
  tipo: string;
  asunto: string;
  estado: 'pendiente' | 'enviado' | 'fallido' | 'rebotado';
  created_at: string;
}
