<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { deixarDeSeguir, obterParlamentar, seguirParlamentar } from '../api/legislation'
import BarrasDeVotos from '../components/BarrasDeVotos.vue'
import MensagemErro from '../components/MensagemErro.vue'
import { useAuth } from '../composables/useAuth'
import { formatarDiaMes } from '../utils/datas'
import { estiloVoto } from '../utils/votos'

const route = useRoute()
const router = useRouter()
const { logado } = useAuth()

const perfil = ref(null)
const carregando = ref(true)
const erro = ref('')
const ocupado = ref(false)

async function carregar() {
  carregando.value = true
  erro.value = ''
  perfil.value = null
  try {
    perfil.value = await obterParlamentar(route.params.id)
  } catch (e) {
    erro.value = e.message
  } finally {
    carregando.value = false
  }
}

async function alternarSeguir() {
  if (!logado.value) return router.push({ name: 'login', query: { redirect: route.fullPath } })
  ocupado.value = true
  try {
    if (perfil.value.seguido) await deixarDeSeguir(perfil.value.id)
    else await seguirParlamentar(perfil.value.id)
    perfil.value.seguido = !perfil.value.seguido
  } catch (e) {
    erro.value = e.message
  } finally {
    ocupado.value = false
  }
}

watch(() => route.params.id, carregar, { immediate: true })
</script>

<template>
  <div class="mx-auto max-w-3xl">
    <RouterLink to="/parlamentares" class="text-sm font-medium text-primaria hover:underline">← Parlamentares</RouterLink>

    <p v-if="carregando" class="py-12 text-center text-slate-500">
      Carregando o perfil… na primeira vez, os votos são buscados na Câmara ou no Senado e podem levar alguns segundos.
    </p>
    <MensagemErro v-else-if="erro && !perfil" class="mt-4" :mensagem="erro" @tentar-novamente="carregar" />

    <template v-else-if="perfil">
      <header class="mt-4 flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5">
        <img
          v-if="perfil.foto_link"
          :src="perfil.foto_link"
          :alt="`Foto de ${perfil.nome}`"
          class="h-20 w-20 rounded-full bg-slate-100 object-cover"
        />
        <span v-else class="h-20 w-20 rounded-full bg-slate-200" />
        <div class="min-w-0 flex-1">
          <h1 class="text-xl font-bold text-slate-900">{{ perfil.nome }}</h1>
          <p class="text-slate-600">
            {{ perfil.casa === 'Senado' ? 'Senador(a)' : 'Deputado(a) federal' }} · {{ perfil.partido }}/{{ perfil.estado }}
          </p>
        </div>
        <button
          type="button"
          :disabled="ocupado"
          class="shrink-0 rounded-lg border px-4 py-2 text-sm font-medium disabled:opacity-50"
          :class="perfil.seguido ? 'border-primaria bg-primaria text-white' : 'border-slate-300 text-slate-700 hover:border-primaria'"
          @click="alternarSeguir"
        >
          {{ perfil.seguido ? 'Seguindo' : 'Seguir' }}
        </button>
      </header>
      <p v-if="erro" class="mt-2 text-sm text-red-600" role="alert">{{ erro }}</p>

      <section class="mt-6">
        <h2 class="text-lg font-semibold text-slate-900">Histórico de posições</h2>
        <p class="mt-1 text-sm text-slate-600">
          Votações nominais dos últimos meses em que o voto de cada parlamentar foi registrado. Votações simbólicas não
          aparecem, porque não guardam o voto individual.
        </p>

        <p v-if="!perfil.votos.length" class="mt-3 rounded-xl border border-dashed border-slate-300 bg-white p-6 text-center text-slate-600">
          Nenhum voto registrado no período.
        </p>
        <template v-else>
          <div class="mt-3 rounded-xl border border-slate-200 bg-white p-4">
            <BarrasDeVotos :contagem="perfil.resumo_votos" />
          </div>
          <ul class="mt-3 space-y-2">
            <li v-for="voto in perfil.votos" :key="voto.id" class="rounded-xl border border-slate-200 bg-white p-4">
              <div class="flex flex-wrap items-center justify-between gap-2">
                <span class="rounded-full px-2 py-0.5 text-xs font-medium" :class="estiloVoto(voto.voto)">{{ voto.voto }}</span>
                <span class="text-xs text-slate-500">{{ formatarDiaMes(voto.data) }} · resultado: {{ voto.status }}</span>
              </div>
              <p v-if="voto.objeto" class="mt-2 font-medium text-slate-900">{{ voto.objeto }}</p>
              <p class="mt-1 text-sm text-slate-700">{{ voto.descricao }}</p>
            </li>
          </ul>
        </template>
      </section>

      <section v-if="perfil.autorias.length" class="mt-6">
        <h2 class="text-lg font-semibold text-slate-900">Projetos de autoria na pauta</h2>
        <ul class="mt-2 space-y-2">
          <li v-for="projeto in perfil.autorias" :key="projeto.id" class="rounded-xl border border-slate-200 bg-white p-4">
            <RouterLink
              :to="{ name: 'agenda', query: { data: projeto.data, projeto: projeto.id } }"
              class="font-medium text-primaria hover:underline"
            >
              {{ projeto.codigo_pl }}
            </RouterLink>
            <span v-if="projeto.data" class="ml-2 text-xs text-slate-500">{{ formatarDiaMes(projeto.data) }}</span>
            <p class="mt-1 line-clamp-2 text-sm text-slate-700">{{ projeto.titulo }}</p>
          </li>
        </ul>
      </section>
    </template>
  </div>
</template>
