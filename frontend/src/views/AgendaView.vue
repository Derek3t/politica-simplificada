<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { obterAgenda } from '../api/legislation'
import DayStrip from '../components/DayStrip.vue'
import DiaEspecialModal from '../components/DiaEspecialModal.vue'
import Icone from '../components/Icone.vue'
import MensagemErro from '../components/MensagemErro.vue'
import ProjetoModal from '../components/ProjetoModal.vue'
import SeletorEstado from '../components/SeletorEstado.vue'
import TimelineItem from '../components/TimelineItem.vue'
import { useAuth } from '../composables/useAuth'
import { useRegiao } from '../composables/useRegiao'
import { ehDataValida, formatarLonga, hoje, somarDias } from '../utils/datas'

const route = useRoute()
const router = useRouter()
const { logado } = useAuth()
const { uf } = useRegiao()

const data = computed(() => (ehDataValida(route.query.data) ? route.query.data : hoje()))
const incluirComissoes = ref(false)
const apenasSeguidos = ref(false)
const agenda = ref(null)
const carregando = ref(false)
const erro = ref('')
const diaAberto = ref(null)
const projetoAbertoId = ref(Number(route.query.projeto) || null)

let ultimaRequisicao = 0

async function carregar() {
  const requisicao = ++ultimaRequisicao
  carregando.value = true
  erro.value = ''
  try {
    const resultado = await obterAgenda(data.value, {
      incluirComissoes: incluirComissoes.value,
      apenasSeguidos: apenasSeguidos.value,
      uf: uf.value,
    })
    if (requisicao === ultimaRequisicao) agenda.value = resultado
  } catch (e) {
    if (requisicao === ultimaRequisicao) erro.value = e.message
  } finally {
    if (requisicao === ultimaRequisicao) carregando.value = false
  }
}

watch([data, incluirComissoes, apenasSeguidos, uf], carregar, { immediate: true })

const ETIQUETAS = { civica: 'Data Cívica', estadual: 'Feriado estadual' }
const etiquetaDoDia = (dia) => (dia.tipo === 'estadual' ? `${ETIQUETAS.estadual} · ${dia.uf}` : (ETIQUETAS[dia.tipo] ?? 'Feriado nacional'))

const irPara = (iso) => router.push({ name: 'agenda', query: { data: iso } })
const vazia = computed(() => agenda.value && !agenda.value.dias_especiais.length && !agenda.value.projetos_lei.length)
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-2">
        <button type="button" class="rounded-lg p-2 hover:bg-slate-200" aria-label="Dia anterior" @click="irPara(somarDias(data, -1))">
          <Icone nome="esquerda" />
        </button>
        <h1 class="text-xl font-bold text-slate-900 sm:text-2xl">{{ formatarLonga(data) }}</h1>
        <button type="button" class="rounded-lg p-2 hover:bg-slate-200" aria-label="Próximo dia" @click="irPara(somarDias(data, 1))">
          <Icone nome="direita" />
        </button>
      </div>
      <input
        type="date"
        :value="data"
        aria-label="Escolher data"
        class="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm"
        @change="ehDataValida($event.target.value) && irPara($event.target.value)"
      />
    </div>

    <div class="mt-4"><DayStrip :data="data" @selecionar="irPara" /></div>

    <div class="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-slate-700">
      <label class="flex items-center gap-2">
        <input v-model="incluirComissoes" type="checkbox" class="h-4 w-4 accent-blue-600" /> Incluir comissões
      </label>
      <label v-if="logado" class="flex items-center gap-2">
        <input v-model="apenasSeguidos" type="checkbox" class="h-4 w-4 accent-blue-600" /> Só de parlamentares que sigo
      </label>
      <SeletorEstado v-model="uf" />
    </div>

    <section class="mt-6">
      <MensagemErro v-if="erro" :mensagem="erro" @tentar-novamente="carregar" />

      <p v-else-if="carregando && !agenda" class="py-12 text-center text-slate-500">
        Buscando dados na Câmara dos Deputados… a primeira consulta de um dia pode levar alguns segundos.
      </p>

      <template v-else-if="agenda">
        <p v-if="carregando" class="mb-3 text-sm text-slate-500">Atualizando…</p>

        <p v-if="vazia" class="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          Nenhuma votação em destaque neste dia.
          <span v-if="!incluirComissoes">Marque “Incluir comissões” para ver as reuniões das comissões.</span>
        </p>

        <ol v-else>
          <TimelineItem
            v-for="dia in agenda.dias_especiais"
            :key="`dia-${dia.id ?? dia.nome}`"
            tipo="dia"
            :etiqueta="etiquetaDoDia(dia)"
            :titulo="dia.nome"
            @abrir="diaAberto = dia"
          />
          <TimelineItem
            v-for="projeto in agenda.projetos_lei"
            :key="`projeto-${projeto.id}`"
            tipo="projeto"
            :etiqueta="`Votação · ${projeto.codigo_pl}`"
            :horario="projeto.horario"
            :titulo="projeto.titulo"
            :descricao="projeto.orgao"
            :destacado="projeto.destacado"
            @abrir="projetoAbertoId = projeto.id"
          />
        </ol>
      </template>
    </section>

    <DiaEspecialModal v-if="diaAberto" :dia="diaAberto" @fechar="diaAberto = null" />
    <ProjetoModal v-if="projetoAbertoId" :projeto-id="projetoAbertoId" @fechar="projetoAbertoId = null" />
  </div>
</template>
