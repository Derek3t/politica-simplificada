<script setup>
defineProps({ mensagem: { type: String, required: true } })
defineEmits(['tentar-novamente'])
</script>

<template>
  <div class="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-800" role="alert">
    <p>{{ mensagem }}</p>
    <button
      type="button"
      class="mt-2 font-medium underline hover:no-underline"
      @click="$emit('tentar-novamente')"
    >
      Tentar novamente
    </button>
  </div>
</template>
