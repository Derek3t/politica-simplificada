import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import AgendaView from '../src/views/AgendaView.vue'

const { obterAgenda, obterVotacao } = vi.hoisted(() => ({ obterAgenda: vi.fn(), obterVotacao: vi.fn() }))

vi.mock('../src/api/legislation', () => ({ obterAgenda, obterVotacao, obterProjeto: vi.fn() }))
vi.mock('../src/composables/useAuth', () => ({ useAuth: () => ({ logado: ref(false) }) }))

const AGENDA = { id: 1, data: '2026-11-12', dias_especiais: [], projetos_lei: [], votacoes: [] }

async function abrir(agenda = {}) {
  obterAgenda.mockResolvedValue({ ...AGENDA, ...agenda })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/agenda', name: 'agenda', component: AgendaView }],
  })
  router.push('/agenda?data=2026-11-12')
  await router.isReady()
  const tela = mount(AgendaView, { global: { plugins: [router] } })
  await flushPromises()
  return tela
}

beforeEach(() => {
  obterAgenda.mockReset()
  obterVotacao.mockReset()
  document.body.innerHTML = ''
})

describe('AgendaView', () => {
  it('mostra a votação do Senado mesmo sem pauta da Câmara', async () => {
    const tela = await abrir({
      votacoes: [{ id: 65, casa: 'Senado', horario: null, objeto: 'PLP 299/2026', descricao: 'Votação nominal do Requerimento.' }],
    })

    expect(tela.text()).toContain('Votação · Senado · PLP 299/2026')
    expect(tela.text()).not.toContain('Nenhuma votação em destaque')
  })

  it('avisa quando o dia não tem nada', async () => {
    const tela = await abrir()

    expect(tela.text()).toContain('Nenhuma votação em destaque neste dia.')
  })
})
