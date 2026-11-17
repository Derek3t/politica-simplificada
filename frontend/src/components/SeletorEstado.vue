<script setup>
import { UFS } from '../composables/useRegiao'

const uf = defineModel({ type: String, default: '' })
</script>

<template>
  <label class="flex items-center gap-2 text-sm text-slate-700">
    Meu estado
    <select v-model="uf" class="rounded-lg border border-slate-300 bg-white px-2 py-1.5 text-sm">
      <option value="">Nenhum</option>
      <option v-for="sigla in UFS" :key="sigla" :value="sigla">{{ sigla }}</option>
    </select>
  </label>
</template>
