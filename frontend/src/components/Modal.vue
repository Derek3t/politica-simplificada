<script setup>
import { onMounted, onUnmounted } from 'vue'
import Icone from './Icone.vue'

const emit = defineEmits(['fechar'])

function aoPressionarTecla(evento) {
  if (evento.key === 'Escape') emit('fechar')
}

onMounted(() => document.addEventListener('keydown', aoPressionarTecla))
onUnmounted(() => document.removeEventListener('keydown', aoPressionarTecla))
</script>

<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-end justify-center bg-marinho/60 sm:items-center sm:p-6"
      @click.self="emit('fechar')"
    >
      <div
        role="dialog"
        aria-modal="true"
        class="relative max-h-[92vh] w-full overflow-y-auto rounded-t-2xl bg-white p-6 shadow-xl sm:max-w-2xl sm:rounded-2xl"
      >
        <button
          type="button"
          class="absolute right-4 top-4 rounded-full p-1 text-slate-500 hover:bg-slate-100"
          aria-label="Fechar"
          @click="emit('fechar')"
        >
          <Icone nome="fechar" />
        </button>
        <slot />
      </div>
    </div>
  </Teleport>
</template>
