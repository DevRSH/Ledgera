import { createRouter, createWebHistory } from 'vue-router';
import MainLayout from '../layouts/MainLayout.vue';
import { useAuthStore } from '../stores/auth.store';

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
          path: 'alumnos/nuevo',
          name: 'AlumnoNuevo',
          component: () => import('../views/alumnos/AlumnoForm.vue'),
          meta: { roles: ['TESORERO', 'SUPER_ADMIN'] }
        },
        {
          path: 'alumnos/:id',
          name: 'AlumnoDetalle',
          component: () => import('../views/alumnos/AlumnoDetalle.vue'),
          props: true
        },
        {
          path: 'alumnos/:id/editar',
          name: 'AlumnoEditar',
          component: () => import('../views/alumnos/AlumnoForm.vue'),
          props: true,
          meta: { roles: ['TESORERO', 'SUPER_ADMIN'] }
        },
        {
          path: 'movimientos',
          name: 'Movimientos',
          component: () => import('../views/movimientos/MovimientoList.vue')
        },
        {
          path: 'conciliacion',
          name: 'Conciliacion',
          component: () => import('../views/conciliacion/ConciliacionBancaria.vue'),
          meta: { roles: ['TESORERO', 'DIRECTIVA', 'SUPER_ADMIN'] }
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
    },
    {
      path: '/public',
      name: 'PanelPublico',
      component: () => import('../views/public/PanelPublico.vue'),
      meta: { public: true }
    },
    {
      path: '/comprobantes/:folio',
      name: 'ComprobanteViewer',
      component: () => import('../views/comprobantes/ComprobanteViewer.vue'),
      meta: { public: true }
    }
  ]
});

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  
  // Public routes
  if (to.meta.public) {
    next();
    return;
  }

  // Authentication check
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' });
    return;
  }

  // Role check
  if (to.meta.roles && Array.isArray(to.meta.roles)) {
    const userRole = authStore.user?.rol;
    if (!userRole || !to.meta.roles.includes(userRole)) {
      next({ name: 'Dashboard' }); // Or a forbidden page
      return;
    }
  }

  // Already logged in
  if (to.name === 'Login' && authStore.isAuthenticated) {
    next({ name: 'Dashboard' });
    return;
  }

  next();
});


export default router;
