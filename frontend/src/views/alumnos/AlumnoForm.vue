<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useForm } from 'vee-validate';
import { toTypedSchema } from '@vee-validate/zod';
import * as zod from 'zod';
import { alumnoService } from '../../services/alumno.service';
// RUT validation should be handled in the frontend or via API call

const props = defineProps<{
  id?: string;
}>();

const router = useRouter();
const loading = ref(false);
const formError = ref('');

// Schema de validación con Zod
const schema = toTypedSchema(zod.object({
  rut: zod.string().min(1, 'El RUT es requerido').refine(val => {
    try {
      // Basic check, ideally we use a JS version of the validator
      return val.length > 7; 
    } catch { return false; }
  }, 'RUT inválido'),
  nombre: zod.string().min(2, 'Nombre muy corto'),
  apellido_paterno: zod.string().min(2, 'Apellido requerido'),
  apellido_materno: zod.string().optional(),
  fecha_nacimiento: zod.string().optional(),
  apoderado_titular: zod.object({
    nombre: zod.string().min(2, 'Nombre requerido'),
    apellido_paterno: zod.string().min(2, 'Apellido requerido'),
    email: zod.string().email('Email inválido'),
    telefono: zod.string().min(8, 'Teléfono inválido'),
  })
}));

const { errors, defineField, handleSubmit, setValues } = useForm({
  validationSchema: schema,
  initialValues: {
    apoderado_titular: {}
  }
});

const [rut] = defineField('rut');
const [nombre] = defineField('nombre');
const [apellido_paterno] = defineField('apellido_paterno');
const [apellido_materno] = defineField('apellido_materno');

const [apoNombre] = defineField('apoderado_titular.nombre');
const [apoApaterno] = defineField('apoderado_titular.apellido_paterno');
const [apoEmail] = defineField('apoderado_titular.email');
const [apoTelefono] = defineField('apoderado_titular.telefono');

onMounted(async () => {
  if (props.id) {
    loading.value = true;
    try {
      const data = await alumnoService.getAlumno(props.id);
      setValues(data);
    } catch (err) {
      console.error(err);
    } finally {
      loading.value = false;
    }
  }
});

const onSubmit = handleSubmit(async (values) => {
  loading.value = true;
  formError.value = '';
  try {
    if (props.id) {
      await alumnoService.actualizarAlumno(props.id, values);
    } else {
      await alumnoService.crearAlumno(values);
    }
    router.push({ name: 'Alumnos' });
  } catch (err: any) {
    console.error(err);
    formError.value = err.response?.data?.detail || 'Error al guardar el alumno. Verifique los datos.';
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="max-w-4xl mx-auto p-6">
    <div class="flex items-center justify-between mb-8">
      <h1 class="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-emerald-300">
        {{ id ? 'Editar Alumno' : 'Nuevo Alumno' }}
      </h1>
      <button 
        @click="router.back()" 
        class="text-slate-400 hover:text-white font-medium transition-colors"
      >
        Cancelar
      </button>
    </div>

    <form @submit="onSubmit" class="space-y-8">
      <!-- Datos Alumno -->
      <section class="bg-slate-900/40 backdrop-blur-md p-6 rounded-xl shadow-xl border border-white/10">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center">
          <span class="w-8 h-8 bg-primary-500/20 text-primary-400 rounded-full flex items-center justify-center mr-3 text-sm shadow-[0_0_10px_rgba(14,165,233,0.3)]">1</span>
          Datos del Alumno
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">RUT</label>
            <input 
              v-model="rut" 
              type="text" 
              placeholder="12.345.678-9"
              class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border focus:ring-2 focus:ring-primary-500 outline-none transition-all text-white placeholder-slate-600"
              :class="errors.rut ? 'border-red-500/50 focus:border-red-500' : 'border-white/10 focus:border-primary-500'"
            />
            <p v-if="errors.rut" class="text-red-500 text-xs mt-1">{{ errors.rut }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Nombres</label>
            <input v-model="nombre" type="text" class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Apellido Paterno</label>
            <input v-model="apellido_paterno" type="text" class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Apellido Materno</label>
            <input v-model="apellido_materno" type="text" class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
        </div>
      </section>

      <!-- Apoderado Titular -->
      <section class="bg-slate-900/40 backdrop-blur-md p-6 rounded-xl shadow-xl border border-white/10">
        <h2 class="text-lg font-semibold text-white mb-4 flex items-center">
          <span class="w-8 h-8 bg-primary-500/20 text-primary-400 rounded-full flex items-center justify-center mr-3 text-sm shadow-[0_0_10px_rgba(14,165,233,0.3)]">2</span>
          Apoderado Titular
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Nombres</label>
            <input v-model="apoNombre" type="text" class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Apellido Paterno</label>
            <input v-model="apoApaterno" type="text" class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Email de Contacto</label>
            <input v-model="apoEmail" type="email" class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-400 mb-1">Teléfono</label>
            <input v-model="apoTelefono" type="text" placeholder="+56 9..." class="w-full px-4 py-2 rounded-lg bg-slate-950/50 border border-white/10 focus:border-primary-500 focus:ring-2 focus:ring-primary-500 outline-none text-white placeholder-slate-600 transition-all" />
          </div>
        </div>
      </section>

      <div v-if="formError" class="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded-lg text-sm mb-4">
        {{ formError }}
      </div>

      <div class="flex justify-end space-x-4">
        <button 
          type="button"
          @click="router.back()"
          class="px-6 py-2 rounded-lg font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          Cancelar
        </button>
        <button 
          type="submit"
          :disabled="loading"
          class="px-8 py-2 bg-gradient-to-r from-primary-600 to-primary-500 text-white rounded-lg font-medium hover:from-primary-500 hover:to-primary-400 shadow-lg shadow-primary-500/25 disabled:opacity-50 transition-all border border-primary-400/20"
        >
          {{ loading ? 'Guardando...' : (id ? 'Guardar Cambios' : 'Crear Alumno') }}
        </button>
      </div>
    </form>
  </div>
</template>
