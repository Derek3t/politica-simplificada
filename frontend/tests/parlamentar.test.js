import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import ParlamentarView from '../src/views/ParlamentarView.vue'

const api = vi.hoisted(() => ({
  obterParlamentar: vi.fn(),
  seguirParlamentar: vi.fn(),
  deixarDeSeguir: vi.fn(),
}))
const estado = vi.hoisted(() => ({ logado: false }))

vi.mock('../src/api/legislation', () => api)
vi.mock('../src/composables/useAuth', () => ({ useAuth: () => ({ logado: ref(estado.logado) }) }))

const PERFIL = {
  id: 5,
  nome: 'Alessandro Vieira',
  casa: 'Senado',
  partido: 'MDB',
  estado: 'SE',
  foto_link: null,
  seguido: false,
  resumo_votos: { Sim: 9, Não: 3 },
  votos: [{ id: 1, voto: 'Sim', data: '2026-11-12', status: 'Aprovado', objeto: 'PLP 299/2026', descricao: 'Emenda 75.' }],
  autorias: [],
}

async function abrir(perfil = {}) {
  api.obterParlamentar.mockResolvedValue({ ...PERFIL, ...perfil })
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/parlamentares', component: { template: '<div />' } },
      { path: '/parlamentares/:id', name: 'parlamentar', component: ParlamentarView },
      { path: '/login', name: 'login', component: { template: '<div />' } },
      { path: '/agenda', name: 'agenda', component: { template: '<div />' } },
    ],
  })
  router.push('/parlamentares/5')
  await router.isReady()
  const tela = mount(ParlamentarView, { global: { plugins: [router] } })
  await flushPromises()
  return { tela, router }
}

beforeEach(() => {
  estado.logado = false
  Object.values(api).forEach((mock) => mock.mockReset())
})

describe('ParlamentarView', () => {
  it('mostra o cabeçalho e o histórico de posições', async () => {
    const { tela } = await abrir()

    expect(api.obterParlamentar).toHaveBeenCalledWith('5')
    expect(tela.text()).toContain('Alessandro Vieira')
    expect(tela.text()).toContain('Senador(a) · MDB/SE')
    expect(tela.text()).toContain('9 (75%)')
    expect(tela.text()).toContain('PLP 299/2026')
  })

  it('avisa quando não há votos nominais no período', async () => {
    const { tela } = await abrir({ votos: [], resumo_votos: {} })

    expect(tela.text()).toContain('Nenhum voto registrado no período.')
  })

  it('lista os projetos de autoria na pauta', async () => {
    const { tela } = await abrir({
      autorias: [{ id: 3, codigo_pl: 'PL 5/2026', titulo: 'Ementa do projeto', data: '2026-11-10' }],
    })

    expect(tela.text()).toContain('PL 5/2026')
    expect(tela.text()).toContain('Ementa do projeto')
  })

  it('manda quem não está logado para o login ao tentar seguir', async () => {
    const { tela, router } = await abrir()

    await tela.find('header button').trigger('click')
    await flushPromises()

    expect(api.seguirParlamentar).not.toHaveBeenCalled()
    expect(router.currentRoute.value.name).toBe('login')
  })

  it('segue e deixa de seguir quando está logado', async () => {
    estado.logado = true
    const { tela } = await abrir()
    const botao = tela.find('header button')

    await botao.trigger('click')
    await flushPromises()
    expect(api.seguirParlamentar).toHaveBeenCalledWith(5)
    expect(botao.text()).toBe('Seguindo')

    await botao.trigger('click')
    await flushPromises()
    expect(api.deixarDeSeguir).toHaveBeenCalledWith(5)
    expect(botao.text()).toBe('Seguir')
  })

  it('mostra o erro quando o perfil não carrega', async () => {
    api.obterParlamentar.mockRejectedValue(new Error('Parlamentar não encontrado.'))
    const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/:id', component: ParlamentarView }] })
    router.push('/5')
    await router.isReady()
    const tela = mount(ParlamentarView, { global: { plugins: [router] } })
    await flushPromises()

    expect(tela.text()).toContain('Parlamentar não encontrado.')
  })
})
