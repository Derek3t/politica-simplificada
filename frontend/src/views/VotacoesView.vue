<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { listarVotacoes } from '../api/legislation'
import MensagemErro from '../components/MensagemErro.vue'
import Paginacao from '../components/Paginacao.vue'
import VotacaoModal from '../components/VotacaoModal.vue'
import { formatarDiaMes } from '../utils/datas'

const PERIODOS = [
  { id: 'hoje', nome: 'Hoje' },
  { id: 'semana', nome: 'Semana' },
  { id: 'mes', nome: 'Mês' },
]
const CASAS = [
  { id: '', nome: 'Câmara e Senado' },
  { id: 'Câmara', nome: 'Câmara' },
  { id: 'Senado', nome: 'Senado' },
]
const STATUS = [
  { id: '', nome: 'Todas' },
  { id: 'aprovado', nome: 'Aprovadas' },
  { id: 'andamento', nome: 'Em andamento' },
  { id: 'rejeitado', nome: 'Rejeitadas' },
]
const ESTILO_STATUS = {
  Aprovado: 'bg-emerald-100 text-emerald-700',
  Rejeitado: 'bg-red-100 text-red-700',
  'Em andamento': 'bg-amber-100 text-amber-700',
}

const route = useRoute()
const periodo = ref(PERIODOS.some((p) => p.id === route.query.periodo) ? route.query.periodo : 'semana')
const status = ref('')
const casa = ref('')
const votacaoAbertaId = ref(null)
const pagina = ref(1)
const itens = ref([])
const totalPaginas = ref(1)
const total = ref(0)
const carregando = ref(false)
const erro = ref('')

let ultimaRequisicao = 0

async function carregar() {
  const requisicao = ++ultimaRequisicao
  carregando.value = true
  erro.value = ''
  try {
    const resposta = await listarVotacoes({ periodo: periodo.value, status: status.value, casa: casa.value, pagina: pagina.value })
    if (requisicao !== ultimaRequisicao) return
    itens.value = resposta.itens
    totalPaginas.value = resposta.total_paginas
    total.value = resposta.total
  } catch (e) {
    if (requisicao === ultimaRequisicao) erro.value = e.message
  } finally {
    if (requisicao === ultimaRequisicao) carregando.value = false
  }
}

watch([periodo, status, casa], () => {
  pagina.value = 1
  carregar()
})
watch(pagina, carregar, { immediate: true })
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <h1 class="text-2xl font-bold text-slate-900">Votações</h1>
    <p class="mt-1 text-slate-600">Acompanhe os projetos votados no Plenário da Câmara e do Senado. Clique em uma votação para ver como cada um votou.</p>

    <div class="mt-5 flex flex-wrap gap-2">
      <button
        v-for="opcao in PERIODOS"
        :key="opcao.id"
        type="button"
        class="rounded-lg px-4 py-1.5 text-sm font-medium"
        :class="periodo === opcao.id ? 'bg-primaria text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
        @click="periodo = opcao.id"
      >
        {{ opcao.nome }}
      </button>
    </div>

    <div class="mt-3 flex flex-wrap gap-2 text-sm">
      <button
        v-for="opcao in CASAS"
        :key="opcao.id"
        type="button"
        class="rounded-full border px-3 py-1"
        :class="casa === opcao.id ? 'border-primaria bg-primaria text-white' : 'border-slate-300 bg-white text-slate-600'"
        @click="casa = opcao.id"
      >
        {{ opcao.nome }}
      </button>
    </div>

    <div class="mt-3 flex flex-wrap gap-2 text-sm">
      <button
        v-for="opcao in STATUS"
        :key="opcao.id"
        type="button"
        class="rounded-full border px-3 py-1"
        :class="status === opcao.id ? 'border-marinho bg-marinho text-white' : 'border-slate-300 bg-white text-slate-600'"
        @click="status = opcao.id"
      >
        {{ opcao.nome }}
      </button>
    </div>

    <section class="mt-5">
      <MensagemErro v-if="erro" :mensagem="erro" @tentar-novamente="carregar" />
      <p v-else-if="carregando && !itens.length" class="py-10 text-center text-slate-500">
        Buscando votações na Câmara e no Senado…
      </p>
      <p v-else-if="!itens.length" class="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
        Nenhuma votação encontrada neste período. Tente ampliar para semana ou mês.
      </p>

      <template v-else>
        <p class="mb-3 text-sm text-slate-500">{{ total }} {{ total === 1 ? 'votação' : 'votações' }}</p>
        <ul class="space-y-3">
          <li v-for="votacao in itens" :key="votacao.id">
            <button
              type="button"
              class="block w-full rounded-xl border border-slate-200 bg-white p-4 text-left shadow-sm transition hover:shadow-md"
              @click="votacaoAbertaId = votacao.id"
            >
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="ESTILO_STATUS[votacao.status]">
                  {{ votacao.status }}
                </span>
                <span class="text-xs text-slate-500">
                  {{ votacao.casa }} · {{ formatarDiaMes(votacao.data) }}<template v-if="votacao.horario"> · {{ votacao.horario }}</template>
                </span>
              </div>
              <h2 v-if="votacao.objeto" class="mt-2 font-semibold text-slate-900">{{ votacao.objeto }}</h2>
              <p class="mt-1 text-sm text-slate-700">{{ votacao.descricao }}</p>
              <span class="mt-2 inline-block text-sm font-medium text-primaria">Ver como votaram →</span>
            </button>
          </li>
        </ul>
      </template>
      <Paginacao :pagina="pagina" :total-paginas="totalPaginas" @mudar="pagina = $event" />
    </section>

    <VotacaoModal v-if="votacaoAbertaId" :votacao-id="votacaoAbertaId" @fechar="votacaoAbertaId = null" />
  </div>
</template>
