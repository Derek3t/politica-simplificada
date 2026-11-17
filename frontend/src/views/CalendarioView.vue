<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { obterCalendario } from '../api/legislation'
import Icone from '../components/Icone.vue'
import MensagemErro from '../components/MensagemErro.vue'
import SeletorEstado from '../components/SeletorEstado.vue'
import { useRegiao } from '../composables/useRegiao'
import { diasDoCalendario, ehMesValido, formatarLonga, formatarMes, hoje, mesDe, somarMeses } from '../utils/datas'

const SEMANA = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']

const route = useRoute()
const router = useRouter()
const { uf } = useRegiao()

const mes = computed(() => (ehMesValido(route.query.mes) ? route.query.mes : mesDe(hoje())))
const dias = ref({})
const carregando = ref(false)
const erro = ref('')
const selecionado = ref(null)

let ultimaRequisicao = 0

async function carregar() {
  const requisicao = ++ultimaRequisicao
  carregando.value = true
  erro.value = ''
  try {
    const resposta = await obterCalendario(mes.value, uf.value)
    if (requisicao === ultimaRequisicao) dias.value = resposta.dias
  } catch (e) {
    if (requisicao === ultimaRequisicao) erro.value = e.message
  } finally {
    if (requisicao === ultimaRequisicao) carregando.value = false
  }
}

watch(uf, carregar)
watch(
  mes,
  () => {
    selecionado.value = mesDe(hoje()) === mes.value ? hoje() : `${mes.value}-01`
    carregar()
  },
  { immediate: true },
)

const celulas = computed(() => diasDoCalendario(mes.value))
const resumo = computed(() => dias.value[selecionado.value] ?? { feriados: [], votacoes: 0, projetos: 0 })
const semConteudo = computed(() => !resumo.value.feriados.length && !resumo.value.votacoes && !resumo.value.projetos)
const irParaMes = (novo) => router.push({ name: 'calendario', query: { mes: novo } })
const numeroDoDia = (iso) => Number(iso.slice(8))
</script>

<template>
  <div class="mx-auto max-w-xl">
    <div class="flex items-center justify-between">
      <button type="button" class="rounded-lg p-2 hover:bg-slate-200" aria-label="Mês anterior" @click="irParaMes(somarMeses(mes, -1))">
        <Icone nome="esquerda" />
      </button>
      <h1 class="text-xl font-bold text-slate-900">{{ formatarMes(mes) }}</h1>
      <button type="button" class="rounded-lg p-2 hover:bg-slate-200" aria-label="Próximo mês" @click="irParaMes(somarMeses(mes, 1))">
        <Icone nome="direita" />
      </button>
    </div>

    <div class="mt-3 flex justify-end"><SeletorEstado v-model="uf" /></div>

    <MensagemErro v-if="erro" class="mt-4" :mensagem="erro" @tentar-novamente="carregar" />

    <div class="mt-4 rounded-2xl border border-slate-200 bg-white p-3 shadow-sm" :class="{ 'opacity-60': carregando }">
      <div class="grid grid-cols-7 text-center text-xs font-medium text-slate-500">
        <span v-for="nome in SEMANA" :key="nome" class="py-2">{{ nome }}</span>
      </div>
      <div class="grid grid-cols-7 gap-1">
        <template v-for="(dia, posicao) in celulas" :key="dia ?? `vazio-${posicao}`">
          <span v-if="dia === null" />
          <button
            v-else
            type="button"
            :aria-pressed="dia === selecionado"
            class="flex aspect-square flex-col items-center justify-center rounded-xl text-sm transition"
            :class="[
              dia === selecionado ? 'bg-primaria font-semibold text-white' : 'text-slate-700 hover:bg-slate-100',
              dia === hoje() && dia !== selecionado ? 'ring-2 ring-primaria' : '',
            ]"
            @click="selecionado = dia"
          >
            {{ numeroDoDia(dia) }}
            <span class="mt-0.5 flex h-1.5 gap-0.5">
              <span v-if="dias[dia]?.feriados.length" class="h-1.5 w-1.5 rounded-full bg-emerald-500" />
              <span v-if="dias[dia]?.votacoes || dias[dia]?.projetos" class="h-1.5 w-1.5 rounded-full bg-violet-500" />
            </span>
          </button>
        </template>
      </div>
      <p class="mt-3 flex items-center justify-center gap-4 text-xs text-slate-500">
        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-emerald-500" /> Feriado ou data cívica</span>
        <span class="flex items-center gap-1"><span class="h-2 w-2 rounded-full bg-violet-500" /> Votações</span>
      </p>
    </div>

    <section v-if="selecionado" class="mt-5">
      <h2 class="font-semibold text-slate-900">Eventos em {{ formatarLonga(selecionado) }}</h2>
      <p v-if="semConteudo" class="mt-2 rounded-xl border border-dashed border-slate-300 bg-white p-4 text-sm text-slate-600">
        Nada registrado neste dia.
      </p>
      <ul v-else class="mt-2 space-y-2 text-sm">
        <li v-for="nome in resumo.feriados" :key="nome" class="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-emerald-900">
          Feriado ou data cívica · <strong>{{ nome }}</strong>
        </li>
        <li v-if="resumo.projetos" class="rounded-xl border border-violet-200 bg-violet-50 p-3 text-violet-900">
          {{ resumo.projetos }} {{ resumo.projetos === 1 ? 'projeto' : 'projetos' }} na pauta do Plenário
        </li>
        <li v-if="resumo.votacoes" class="rounded-xl border border-violet-200 bg-violet-50 p-3 text-violet-900">
          {{ resumo.votacoes }} {{ resumo.votacoes === 1 ? 'votação realizada' : 'votações realizadas' }}
        </li>
      </ul>
      <RouterLink
        :to="{ name: 'agenda', query: { data: selecionado } }"
        class="mt-3 inline-block text-sm font-medium text-primaria hover:underline"
      >
        Abrir agenda deste dia →
      </RouterLink>
    </section>
  </div>
</template>
