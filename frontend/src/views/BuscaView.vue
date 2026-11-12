<script setup>
import { computed, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { buscar, deixarDeSeguir, seguirParlamentar } from '../api/legislation'
import Icone from '../components/Icone.vue'
import MensagemErro from '../components/MensagemErro.vue'
import ParlamentarCard from '../components/ParlamentarCard.vue'
import { useAuth } from '../composables/useAuth'
import { formatarLonga } from '../utils/datas'

const route = useRoute()
const router = useRouter()
const { logado } = useAuth()

const termo = ref(String(route.query.q || ''))
const resultado = ref(null)
const carregando = ref(false)
const erro = ref('')
const ocupadoId = ref(null)

let temporizador
let ultimaRequisicao = 0

async function carregar() {
  const consulta = termo.value.trim()
  const requisicao = ++ultimaRequisicao
  if (consulta.length < 2) {
    resultado.value = null
    carregando.value = false
    return
  }
  carregando.value = true
  erro.value = ''
  try {
    const resposta = await buscar(consulta)
    if (requisicao === ultimaRequisicao) resultado.value = resposta
  } catch (e) {
    if (requisicao === ultimaRequisicao) erro.value = e.message
  } finally {
    if (requisicao === ultimaRequisicao) carregando.value = false
  }
}

async function alternarSeguir(parlamentar) {
  if (!logado.value) return router.push({ name: 'login', query: { redirect: route.fullPath } })
  ocupadoId.value = parlamentar.id
  try {
    if (parlamentar.seguido) await deixarDeSeguir(parlamentar.id)
    else await seguirParlamentar(parlamentar.id)
    parlamentar.seguido = !parlamentar.seguido
  } catch (e) {
    erro.value = e.message
  } finally {
    ocupadoId.value = null
  }
}

const vazio = computed(() => resultado.value && Object.values(resultado.value).every((lista) => !lista.length))

watch(termo, () => {
  clearTimeout(temporizador)
  temporizador = setTimeout(() => {
    router.replace({ query: termo.value.trim() ? { q: termo.value.trim() } : {} })
    carregar()
  }, 300)
})
carregar()
onUnmounted(() => clearTimeout(temporizador))
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <h1 class="text-2xl font-bold text-slate-900">Busca</h1>
    <p class="mt-1 text-slate-600">Procure por deputados, projetos de lei, votações e datas cívicas.</p>

    <label class="relative mt-5 block">
      <span class="sr-only">Termo de busca</span>
      <Icone nome="busca" :tamanho="18" class="absolute left-3 top-3 text-slate-400" />
      <input
        v-model="termo"
        type="search"
        placeholder="Ex.: transporte, PL 10/2026, nome de deputado…"
        class="w-full rounded-lg border border-slate-300 bg-white py-2.5 pl-10 pr-3 outline-none focus:ring-2 focus:ring-primaria"
      />
    </label>

    <section class="mt-6 space-y-6">
      <MensagemErro v-if="erro" :mensagem="erro" @tentar-novamente="carregar" />
      <p v-else-if="carregando && !resultado" class="py-10 text-center text-slate-500">Buscando…</p>
      <p v-else-if="!resultado" class="py-10 text-center text-slate-500">Digite pelo menos 2 letras para buscar.</p>
      <p v-else-if="vazio" class="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
        Nada encontrado para “{{ termo }}”. A busca olha apenas dados já consultados no app.
      </p>

      <template v-else>
        <div v-if="resultado.parlamentares.length">
          <h2 class="mb-2 font-semibold text-slate-900">Parlamentares</h2>
          <ul class="space-y-2">
            <ParlamentarCard
              v-for="parlamentar in resultado.parlamentares"
              :key="parlamentar.id"
              :parlamentar="parlamentar"
              :ocupado="ocupadoId === parlamentar.id"
              @alternar-seguir="alternarSeguir"
            />
          </ul>
        </div>

        <div v-if="resultado.projetos.length">
          <h2 class="mb-2 font-semibold text-slate-900">Projetos de lei</h2>
          <ul class="space-y-2">
            <li v-for="projeto in resultado.projetos" :key="projeto.id">
              <RouterLink
                :to="{ name: 'agenda', query: { data: projeto.data, projeto: projeto.id } }"
                class="block rounded-xl border border-slate-200 bg-white p-3 hover:border-primaria"
              >
                <p class="text-sm font-medium text-primaria">{{ projeto.codigo_pl }} · {{ formatarLonga(projeto.data) }}</p>
                <p class="mt-1 line-clamp-2 text-slate-800">{{ projeto.titulo }}</p>
              </RouterLink>
            </li>
          </ul>
        </div>

        <div v-if="resultado.votacoes.length">
          <h2 class="mb-2 font-semibold text-slate-900">Votações</h2>
          <ul class="space-y-2">
            <li v-for="votacao in resultado.votacoes" :key="votacao.id">
              <RouterLink
                :to="{ name: 'agenda', query: { data: votacao.data } }"
                class="block rounded-xl border border-slate-200 bg-white p-3 hover:border-primaria"
              >
                <p class="text-sm font-medium text-slate-500">
                  {{ votacao.objeto || 'Votação' }} · {{ formatarLonga(votacao.data) }} · {{ votacao.status }}
                </p>
                <p class="mt-1 line-clamp-2 text-slate-800">{{ votacao.descricao }}</p>
              </RouterLink>
            </li>
          </ul>
        </div>

        <div v-if="resultado.dias_especiais.length">
          <h2 class="mb-2 font-semibold text-slate-900">Feriados e datas cívicas</h2>
          <ul class="space-y-2">
            <li v-for="dia in resultado.dias_especiais" :key="dia.id">
              <RouterLink
                :to="{ name: 'agenda', query: { data: dia.data } }"
                class="block rounded-xl border border-slate-200 bg-white p-3 hover:border-primaria"
              >
                <p class="font-medium text-slate-800">{{ dia.nome }}</p>
                <p class="text-sm text-slate-500">{{ formatarLonga(dia.data) }}</p>
              </RouterLink>
            </li>
          </ul>
        </div>
      </template>
    </section>
  </div>
</template>
