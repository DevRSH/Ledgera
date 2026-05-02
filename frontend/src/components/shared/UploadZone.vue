<script setup lang="ts">
import { ref } from 'vue';

const props = withDefaults(defineProps<{
  accept?: string;
  maxSizeMb?: number;
  multiple?: boolean;
}>(), {
  accept: 'image/*,application/pdf',
  maxSizeMb: 10,
  multiple: false
});

const emit = defineEmits<{
  (e: 'file-selected', files: File[]): void;
}>();

const isDragging = ref(false);
const error = ref<string | null>(null);
const selectedFiles = ref<File[]>([]);
const fileInput = ref<HTMLInputElement | null>(null);

const handleDrop = (e: DragEvent) => {
  isDragging.value = false;
  const files = e.dataTransfer?.files;
  if (files) processFiles(Array.from(files));
};

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement;
  if (target.files) processFiles(Array.from(target.files));
};

const processFiles = (files: File[]) => {
  error.value = null;
  const validFiles: File[] = [];

  for (const file of files) {
    // Validate size
    if (file.size > props.maxSizeMb * 1024 * 1024) {
      error.value = `El archivo ${file.name} excede los ${props.maxSizeMb}MB permitidos.`;
      return;
    }
    validFiles.push(file);
  }

  selectedFiles.value = props.multiple ? [...selectedFiles.value, ...validFiles] : validFiles;
  emit('file-selected', selectedFiles.value);
};

const removeFile = (index: number) => {
  selectedFiles.value.splice(index, 1);
  emit('file-selected', selectedFiles.value);
};
</script>

<template>
  <div class="w-full">
    <div 
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      @click="fileInput?.click()"
      class="border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-all"
      :class="[
        isDragging ? 'border-emerald-500 bg-emerald-50' : 'border-slate-300 hover:border-emerald-400 hover:bg-slate-50',
        error ? 'border-red-500 bg-red-50' : ''
      ]"
    >
      <input 
        type="file" 
        ref="fileInput" 
        class="hidden" 
        :accept="accept" 
        :multiple="multiple"
        @change="handleFileInput"
      >
      
      <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-slate-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      
      <p class="text-slate-600 font-medium">Haz clic o arrastra archivos aquí</p>
      <p class="text-slate-400 text-sm mt-1">{{ accept }} (Máx. {{ maxSizeMb }}MB)</p>
      
      <p v-if="error" class="mt-2 text-sm text-red-600 font-semibold">{{ error }}</p>
    </div>

    <!-- Previews -->
    <div v-if="selectedFiles.length > 0" class="mt-4 space-y-2">
      <div 
        v-for="(file, index) in selectedFiles" 
        :key="index"
        class="flex items-center justify-between p-2 bg-white border border-slate-200 rounded shadow-sm"
      >
        <div class="flex items-center space-x-3 truncate">
          <div class="p-2 bg-slate-100 rounded">
            <svg v-if="file.type === 'application/pdf'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
          <div class="truncate">
            <p class="text-sm font-medium text-slate-700 truncate">{{ file.name }}</p>
            <p class="text-xs text-slate-400">{{ (file.size / 1024).toFixed(1) }} KB</p>
          </div>
        </div>
        <button @click="removeFile(index)" class="p-1 text-slate-400 hover:text-red-500 transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
