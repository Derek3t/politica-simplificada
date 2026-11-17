<script setup>
import { computed } from 'vue'
import { estiloVoto, porcentagens } from '../utils/votos'

const props = defineProps({ contagem: { type: Object, required: true } })
const linhas = computed(() => porcentagens(props.contagem))
</script>

<template>
  <ul class="space-y-2">
    <li v-for="linha in linhas" :key="linha.voto" class="text-sm">
      <div class="flex justify-between text-slate-700">
        <span>{{ linha.voto }}</span>
        <span>{{ linha.quantidade }} ({{ linha.percentual }}%)</span>
      </div>
      <div class="mt-1 h-2 rounded-full bg-slate-100">
        <div class="h-2 rounded-full" :class="estiloVoto(linha.voto)" :style="{ width: `${linha.percentual}%` }" />
      </div>
    </li>
  </ul>
</template>
