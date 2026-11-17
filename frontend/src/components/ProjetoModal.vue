<script setup>
import { onMounted, ref } from 'vue'
import { adicionarAoGoogle, analisarProjeto, obterProjeto, urlCalendario } from '../api/legislation'
import { useAuth } from '../composables/useAuth'
import Icone from './Icone.vue'
import MensagemErro from './MensagemErro.vue'
import Modal from './Modal.vue'

const props = defineProps({ projetoId: { type: Number, required: true } })
defineEmits(['fechar'])

const { logado, usuario } = useAuth()
const projeto = ref(null)
const carregando = ref(true)
const analisando = ref(false)
const erro = ref('')
const agendando = ref(false)
const linkEvento = ref('')
const erroGoogle = ref('')

async function executar(acao, estado) {
  estado.value = true
  erro.value = ''
  try {
    projeto.value = await acao()
  } catch (e) {
    erro.value = e.message
  } finally {
    estado.value = false
  }
}

const carregar = () => executar(() => obterProjeto(props.projetoId), carregando)
const analisar = () => executar(() => analisarProjeto(props.projetoId), analisando)

async function adicionarNoGoogle() {
  agendando.value = true
  erroGoogle.value = ''
  try {
    linkEvento.value = (await adicionarAoGoogle(props.projetoId)).link
  } catch (e) {
    erroGoogle.value = e.message
  } finally {
    agendando.value = false
  }
}

onMounted(carregar)
</script>

<template>
  <Modal @fechar="$emit('fechar')">
    <p v-if="carregando" class="py-10 text-center text-slate-500">Carregando…</p>
    <MensagemErro v-else-if="!projeto" :mensagem="erro" @tentar-novamente="carregar" />

    <template v-else>
      <span class="rounded-full bg-violet-100 px-2 py-0.5 text-xs font-medium text-violet-700">
        Votação no Congresso · {{ projeto.codigo_pl }}
      </span>
      <h2 class="mt-3 pr-8 text-lg font-bold leading-snug text-slate-900">{{ projeto.titulo }}</h2>
      <p class="mt-2 text-sm text-slate-500">{{ projeto.orgao }} · {{ projeto.status }}</p>

      <section v-if="projeto.resumo" class="mt-5 space-y-4">
        <div>
          <h3 class="font-semibold text-slate-900">O que significa?</h3>
          <p class="mt-1 text-slate-700">{{ projeto.resumo }}</p>
        </div>
        <div>
          <h3 class="font-semibold text-slate-900">Impacto prático</h3>
          <p class="mt-1 text-slate-700">{{ projeto.analise_impacto }}</p>
        </div>
        <div class="rounded-xl border border-blue-100 bg-blue-50 p-4">
          <h3 class="text-sm font-semibold text-blue-800">Panorama internacional</h3>
          <p class="mt-1 text-sm text-blue-900">{{ projeto.comparacao_internacional }}</p>
        </div>
      </section>

      <div v-else class="mt-5">
        <MensagemErro v-if="erro" :mensagem="erro" @tentar-novamente="analisar" />
        <button
          v-else-if="logado"
          type="button"
          :disabled="analisando"
          class="rounded-lg bg-primaria px-4 py-2 font-medium text-white disabled:opacity-60"
          @click="analisar"
        >
          {{ analisando ? 'Traduzindo o juridiquês…' : 'Resumir em linguagem simples' }}
        </button>
        <p v-else class="text-sm text-slate-600">
          <RouterLink to="/login" class="font-medium text-primaria underline">Entre</RouterLink>
          para gerar o resumo com IA.
        </p>
      </div>

      <section v-if="projeto.parlamentares.length" class="mt-6">
        <h3 class="font-semibold text-slate-900">Parlamentares envolvidos</h3>
        <ul class="mt-2 space-y-1 text-sm text-slate-700">
          <li v-for="p in projeto.parlamentares" :key="p.id">
            {{ p.nome }} ({{ p.partido }}/{{ p.estado }}) <span class="text-slate-500">· {{ p.posicionamento }}</span>
          </li>
        </ul>
      </section>

      <div v-if="logado" class="mt-6 flex flex-wrap items-center gap-3">
        <button
          v-if="usuario.google_calendar"
          type="button"
          :disabled="agendando || linkEvento !== ''"
          class="inline-flex items-center gap-2 rounded-lg bg-primaria px-4 py-2 text-sm font-medium text-white disabled:opacity-60"
          @click="adicionarNoGoogle"
        >
          <Icone nome="calendario" :tamanho="16" />
          {{ agendando ? 'Adicionando…' : linkEvento ? 'Adicionado!' : 'Adicionar ao Google Calendar' }}
        </button>
        <a
          :href="urlCalendario(projeto.id)"
          class="inline-flex items-center gap-2 rounded-lg border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:border-primaria hover:text-primaria"
        >
          <Icone nome="baixar" :tamanho="16" /> Baixar .ics
        </a>
      </div>
      <p v-if="linkEvento" class="mt-2 text-sm">
        <a :href="linkEvento" target="_blank" rel="noopener" class="font-medium text-primaria underline">Abrir evento no Google Calendar</a>
      </p>
      <p v-if="erroGoogle" class="mt-2 text-sm text-red-600" role="alert">{{ erroGoogle }}</p>
    </template>
  </Modal>
</template>
