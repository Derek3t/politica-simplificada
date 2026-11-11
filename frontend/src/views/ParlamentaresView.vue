<script setup>
import { onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deixarDeSeguir, listarParlamentares, listarSeguidos, seguirParlamentar } from '../api/legislation'
import Icone from '../components/Icone.vue'
import MensagemErro from '../components/MensagemErro.vue'
import ParlamentarCard from '../components/ParlamentarCard.vue'
import { useAuth } from '../composables/useAuth'

const UFS = 'AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split(' ')

const route = useRoute()
const router = useRouter()
const { logado } = useAuth()

const aba = ref('todos')
const busca = ref('')
const estado = ref('')
const pagina = ref(1)
const itens = ref([])
const totalPaginas = ref(1)
const carregando = ref(false)
const erro = ref('')
const ocupadoId = ref(null)

let temporizador
let ultimaRequisicao = 0

async function carregar() {
  const requisicao = ++ultimaRequisicao
  carregando.value = true
  erro.value = ''
  try {
    if (aba.value === 'seguidos') {
      itens.value = (await listarSeguidos()).itens
      totalPaginas.value = 1
    } else {
      const resposta = await listarParlamentares({ busca: busca.value, estado: estado.value, pagina: pagina.value })
      if (requisicao !== ultimaRequisicao) return
      itens.value = resposta.itens
      totalPaginas.value = resposta.total_paginas
    }
  } catch (e) {
    if (requisicao === ultimaRequisicao) erro.value = e.message
  } finally {
    if (requisicao === ultimaRequisicao) carregando.value = false
  }
}

function selecionarAba(nova) {
  if (nova === 'seguidos' && !logado.value) return irParaLogin()
  aba.value = nova
}

const irParaLogin = () => router.push({ name: 'login', query: { redirect: route.fullPath } })

async function alternarSeguir(parlamentar) {
  if (!logado.value) return irParaLogin()
  ocupadoId.value = parlamentar.id
  try {
    if (parlamentar.seguido) await deixarDeSeguir(parlamentar.id)
    else await seguirParlamentar(parlamentar.id)
    parlamentar.seguido = !parlamentar.seguido
    if (aba.value === 'seguidos') itens.value = itens.value.filter((p) => p.seguido)
  } catch (e) {
    erro.value = e.message
  } finally {
    ocupadoId.value = null
  }
}

watch([busca, estado], () => {
  clearTimeout(temporizador)
  temporizador = setTimeout(() => {
    pagina.value = 1
    carregar()
  }, 300)
})
watch([aba, pagina], carregar, { immediate: true })
onUnmounted(() => clearTimeout(temporizador))
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <h1 class="text-2xl font-bold text-slate-900">Parlamentares</h1>
    <p class="mt-1 text-slate-600">Veja quem são os deputados e acompanhe os que mais importam para você.</p>

    <div class="mt-5 flex gap-2">
      <button
        v-for="opcao in [{ id: 'todos', nome: 'Todos' }, { id: 'seguidos', nome: 'Seguindo' }]"
        :key="opcao.id"
        type="button"
        class="rounded-lg px-4 py-1.5 text-sm font-medium"
        :class="aba === opcao.id ? 'bg-primaria text-white' : 'bg-white text-slate-700 hover:bg-slate-100'"
        @click="selecionarAba(opcao.id)"
      >
        {{ opcao.nome }}
      </button>
    </div>

    <div v-if="aba === 'todos'" class="mt-4 flex flex-col gap-3 sm:flex-row">
      <label class="relative flex-1">
        <span class="sr-only">Buscar por nome</span>
        <Icone nome="busca" :tamanho="18" class="absolute left-3 top-2.5 text-slate-400" />
        <input
          v-model="busca"
          type="search"
          placeholder="Buscar por nome…"
          class="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 outline-none focus:ring-2 focus:ring-primaria"
        />
      </label>
      <select v-model="estado" aria-label="Estado" class="rounded-lg border border-slate-300 bg-white px-3 py-2">
        <option value="">Todos os estados</option>
        <option v-for="uf in UFS" :key="uf" :value="uf">{{ uf }}</option>
      </select>
    </div>

    <section class="mt-5">
      <MensagemErro v-if="erro" :mensagem="erro" @tentar-novamente="carregar" />
      <p v-else-if="carregando && !itens.length" class="py-10 text-center text-slate-500">Carregando…</p>
      <p v-else-if="!itens.length" class="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
        {{ aba === 'seguidos' ? 'Você ainda não segue nenhum parlamentar.' : 'Nenhum parlamentar encontrado.' }}
      </p>

      <ul v-else class="space-y-2">
        <ParlamentarCard
          v-for="parlamentar in itens"
          :key="parlamentar.id"
          :parlamentar="parlamentar"
          :ocupado="ocupadoId === parlamentar.id"
          @alternar-seguir="alternarSeguir"
        />
      </ul>

      <div v-if="totalPaginas > 1" class="mt-5 flex items-center justify-center gap-4 text-sm">
        <button type="button" :disabled="pagina <= 1" class="rounded-lg bg-white px-3 py-1.5 disabled:opacity-40" @click="pagina--">
          Anterior
        </button>
        <span class="text-slate-600">Página {{ pagina }} de {{ totalPaginas }}</span>
        <button type="button" :disabled="pagina >= totalPaginas" class="rounded-lg bg-white px-3 py-1.5 disabled:opacity-40" @click="pagina++">
          Próxima
        </button>
      </div>
    </section>
  </div>
</template>
