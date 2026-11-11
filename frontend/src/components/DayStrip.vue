<script setup>
import { computed } from 'vue'
import { formatarDiaMes, formatarDiaSemana, hoje, somarDias } from '../utils/datas'

const props = defineProps({ data: { type: String, required: true } })
const emit = defineEmits(['selecionar'])

const dias = computed(() => Array.from({ length: 7 }, (_, i) => somarDias(props.data, i - 3)))
</script>

<template>
  <div class="flex gap-2 overflow-x-auto pb-1" role="tablist">
    <button
      v-for="dia in dias"
      :key="dia"
      type="button"
      role="tab"
      :aria-selected="dia === data"
      class="min-w-20 flex-1 rounded-xl border px-3 py-2 text-center text-sm transition"
      :class="
        dia === data
          ? 'border-primaria bg-primaria text-white shadow'
          : 'border-slate-200 bg-white text-slate-600 hover:border-primaria'
      "
      @click="emit('selecionar', dia)"
    >
      <span class="block font-medium capitalize">{{ dia === hoje() ? 'Hoje' : formatarDiaSemana(dia) }}</span>
      <span class="block text-xs opacity-80">{{ formatarDiaMes(dia) }}</span>
    </button>
  </div>
</template>
