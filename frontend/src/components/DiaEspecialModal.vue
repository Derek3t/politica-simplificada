<script setup>
import { ref } from 'vue'
import { contextualizarDia } from '../api/legislation'
import { useAuth } from '../composables/useAuth'
import { formatarLonga } from '../utils/datas'
import MensagemErro from './MensagemErro.vue'
import Modal from './Modal.vue'

const props = defineProps({ dia: { type: Object, required: true } })
defineEmits(['fechar'])

const { logado } = useAuth()
const dia = ref({ ...props.dia })
const carregando = ref(false)
const erro = ref('')

async function gerarContexto() {
  carregando.value = true
  erro.value = ''
  try {
    dia.value = await contextualizarDia(dia.value.id)
  } catch (e) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <Modal @fechar="$emit('fechar')">
    <span class="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">Feriado / Data Cívica</span>
    <p class="mt-2 text-sm text-slate-500">{{ formatarLonga(dia.data) }}</p>
    <h2 class="mt-1 pr-8 text-2xl font-bold text-slate-900">{{ dia.nome }}</h2>

    <template v-if="dia.contexto_historico">
      <p class="mt-4 text-slate-700">{{ dia.contexto_historico }}</p>
      <h3 class="mt-5 font-semibold text-slate-900">Por que é importante?</h3>
      <p class="mt-1 text-slate-700">{{ dia.importancia }}</p>
      <div class="mt-5 rounded-xl border border-blue-100 bg-blue-50 p-4">
        <h3 class="text-sm font-semibold text-blue-800">Impacto legislativo e social</h3>
        <p class="mt-1 text-sm text-blue-900">{{ dia.impacto_legislativo }}</p>
      </div>
    </template>

    <div v-else class="mt-5">
      <MensagemErro v-if="erro" :mensagem="erro" @tentar-novamente="gerarContexto" />
      <button
        v-else-if="logado"
        type="button"
        :disabled="carregando"
        class="rounded-lg bg-primaria px-4 py-2 font-medium text-white disabled:opacity-60"
        @click="gerarContexto"
      >
        {{ carregando ? 'Gerando explicação…' : 'Explicar esta data com IA' }}
      </button>
      <p v-else class="text-sm text-slate-600">
        <RouterLink to="/login" class="font-medium text-primaria underline">Entre</RouterLink>
        para ver o significado histórico desta data.
      </p>
    </div>
  </Modal>
</template>
