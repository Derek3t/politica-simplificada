<script setup>
defineProps({
  rotulo: { type: String, required: true },
  tipo: { type: String, default: 'text' },
  erro: { type: String, default: '' },
  autocomplete: { type: String, default: 'off' },
})

const modelo = defineModel({ type: String, default: '' })
</script>

<template>
  <label class="block text-sm font-medium text-slate-700">
    {{ rotulo }}
    <input
      v-model="modelo"
      :type="tipo"
      :autocomplete="autocomplete"
      :aria-invalid="erro !== ''"
      class="mt-1 block w-full rounded-lg border px-3 py-2 text-slate-900 outline-none focus:ring-2 focus:ring-primaria"
      :class="erro ? 'border-red-400' : 'border-slate-300'"
    />
    <span v-if="erro" class="mt-1 block text-sm text-red-600" role="alert">{{ erro }}</span>
  </label>
</template>
