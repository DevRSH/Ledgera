import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layouts/MainLayout.vue';


const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/auth/Login.vue'),
      meta: { public: true }
    },
    {
      path: '/login/2fa',
      name: 'Login2FA',
      component: () => import('../views/auth/Login2FA.vue'),
      meta: { public: true }
    },
    {
      path: '/',
      component: MainLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Dashboard',
          component: () => import('../views/Dashboard.vue')
        },
        {
          path: 'alumnos',
          name: 'Alumnos',
          component: () => import('../views/alumnos/AlumnoList.vue')
        },
        {
          path: 'cuotas',
          name: 'Cuotas',
          component: () => import('../views/cuotas/CuotaPanel.vue')
        },
        {
          path: 'documentos',
          name: 'Documentos',
          component: () => import('../views/DocumentoGestoria.vue')
        },
        {
          path: 'comunicaciones',
          name: 'Comunicaciones',
          component: () => import('../views/HistorialComunicaciones.vue')
        },
        {
          path: 'reportes',
          name: 'Reportes',
          component: () => import('../views/ReportesPanel.vue')
        },
        {
          path: 'auditoria',
          name: 'Auditoria',
          component: () => import('../views/AuditLog.vue')
        }





      ]
    }
  ]
});

router.beforeEach(async (to, _from, next) => {
  // Login Bypass: Always allow access
  if (to.name === 'Login' && !to.query.forced) {
    next({ name: 'Dashboard' });
  } else {
    next();
  }
});


export default router;
