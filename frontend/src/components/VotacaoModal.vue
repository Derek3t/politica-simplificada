<script setup>
import { onMounted, ref } from 'vue'
import { obterVotacao } from '../api/legislation'
import { useAuth } from '../composables/useAuth'
import { formatarDiaMes } from '../utils/datas'
import { estiloVoto } from '../utils/votos'
import BarrasDeVotos from './BarrasDeVotos.vue'
import MensagemErro from './MensagemErro.vue'
import Modal from './Modal.vue'

const props = defineProps({ votacaoId: { type: Number, required: true } })
defineEmits(['fechar'])

const { logado } = useAuth()
const votacao = ref(null)
const carregando = ref(true)
const erro = ref('')

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    votacao.value = await obterVotacao(props.votacaoId)
  } catch (e) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <Modal @fechar="$emit('fechar')">
    <p v-if="carregando" class="py-10 text-center text-slate-500">Buscando os votos…</p>
    <MensagemErro v-else-if="erro" :mensagem="erro" @tentar-novamente="carregar" />

    <template v-else>
      <p class="text-sm text-slate-500">{{ votacao.casa }} · {{ formatarDiaMes(votacao.data) }} · {{ votacao.status }}</p>
      <h2 v-if="votacao.objeto" class="mt-1 pr-8 text-lg font-bold text-slate-900">{{ votacao.objeto }}</h2>
      <p class="mt-2 text-slate-700">{{ votacao.descricao }}</p>

      <section class="mt-5">
        <h3 class="font-semibold text-slate-900">Como o plenário votou</h3>
        <BarrasDeVotos v-if="votacao.nominal" class="mt-2" :contagem="votacao.placar" />
        <p v-else class="mt-1 text-sm text-slate-600">
          Votação simbólica: o resultado é declarado pela presidência, sem registrar o voto de cada parlamentar.
        </p>
      </section>

      <section v-if="votacao.nominal" class="mt-5">
        <h3 class="font-semibold text-slate-900">Parlamentares que você segue</h3>
        <p v-if="!logado" class="mt-1 text-sm text-slate-600">
          <RouterLink to="/login" class="font-medium text-primaria underline">Entre</RouterLink>
          para ver como os parlamentares que você segue votaram.
        </p>
        <p v-else-if="!votacao.votos_seguidos.length" class="mt-1 text-sm text-slate-600">
          Nenhum parlamentar que você segue votou nesta votação.
        </p>
        <ul v-else class="mt-2 space-y-1 text-sm">
          <li v-for="p in votacao.votos_seguidos" :key="p.id" class="flex items-center justify-between gap-2">
            <RouterLink :to="{ name: 'parlamentar', params: { id: p.id } }" class="text-slate-800 hover:underline">
              {{ p.nome }} ({{ p.partido }}/{{ p.estado }})
            </RouterLink>
            <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="estiloVoto(p.voto)">{{ p.voto }}</span>
          </li>
        </ul>
      </section>
    </template>
  </Modal>
</template>
