<script setup>
defineProps({
  pagina: { type: Number, required: true },
  totalPaginas: { type: Number, required: true },
})
defineEmits(['mudar'])
</script>

<template>
  <nav v-if="totalPaginas > 1" class="mt-5 flex items-center justify-center gap-4 text-sm" aria-label="Paginação">
    <button type="button" :disabled="pagina <= 1" class="rounded-lg bg-white px-3 py-1.5 disabled:opacity-40" @click="$emit('mudar', pagina - 1)">
      Anterior
    </button>
    <span class="text-slate-600">Página {{ pagina }} de {{ totalPaginas }}</span>
    <button
      type="button"
      :disabled="pagina >= totalPaginas"
      class="rounded-lg bg-white px-3 py-1.5 disabled:opacity-40"
      @click="$emit('mudar', pagina + 1)"
    >
      Próxima
    </button>
  </nav>
</template>
