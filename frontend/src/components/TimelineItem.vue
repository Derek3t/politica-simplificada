<script setup>
defineProps({
  horario: { type: String, default: null },
  tipo: { type: String, required: true },
  etiqueta: { type: String, required: true },
  titulo: { type: String, required: true },
  descricao: { type: String, default: '' },
  destacado: { type: Boolean, default: false },
})
defineEmits(['abrir'])

const CORES = {
  projeto: 'bg-violet-100 text-violet-700',
  dia: 'bg-emerald-100 text-emerald-700',
  votacao: 'bg-sky-100 text-sky-700',
}
</script>

<template>
  <li class="flex gap-3 sm:gap-5">
    <span class="w-12 shrink-0 pt-4 text-right text-sm font-medium text-slate-500">{{ horario ?? 'Dia todo' }}</span>
    <div class="relative flex-1 border-l-2 border-slate-200 pb-4 pl-5">
      <span class="absolute -left-[7px] top-5 h-3 w-3 rounded-full border-2 border-primaria bg-white" />
      <button
        type="button"
        class="block w-full rounded-xl border bg-white p-4 text-left shadow-sm transition hover:shadow-md"
        :class="destacado ? 'border-amber-400 ring-1 ring-amber-300' : 'border-slate-200'"
        @click="$emit('abrir')"
      >
        <span class="inline-block rounded-full px-2 py-0.5 text-xs font-medium" :class="CORES[tipo]">
          {{ etiqueta }}
        </span>
        <span v-if="destacado" class="ml-2 text-xs font-medium text-amber-600">Parlamentar que você segue</span>
        <h3 class="mt-2 line-clamp-2 font-semibold text-slate-900">{{ titulo }}</h3>
        <p v-if="descricao" class="mt-1 line-clamp-2 text-sm text-slate-600">{{ descricao }}</p>
        <span class="mt-2 inline-block text-sm font-medium text-primaria">Ver detalhes →</span>
      </button>
    </div>
  </li>
</template>
