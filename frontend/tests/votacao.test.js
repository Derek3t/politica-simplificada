import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import VotacaoModal from '../src/components/VotacaoModal.vue'

const { logado, obterVotacao } = vi.hoisted(() => ({ logado: { value: false }, obterVotacao: vi.fn() }))

vi.mock('../src/api/legislation', () => ({ obterVotacao }))
vi.mock('../src/composables/useAuth', () => ({ useAuth: () => ({ logado: ref(logado.value) }) }))

const VOTACAO = {
  id: 1,
  casa: 'Senado',
  data: '2026-11-12',
  status: 'Aprovado',
  objeto: 'PLP 299/2026',
  descricao: 'Votação nominal da emenda.',
  nominal: true,
  placar: { Sim: 45, Não: 31 },
  votos_seguidos: [],
}

const RouterLinkStub = { props: ['to'], template: '<a><slot /></a>' }

async function abrir(votacao) {
  obterVotacao.mockResolvedValue({ ...VOTACAO, ...votacao })
  const modal = mount(VotacaoModal, {
    props: { votacaoId: 1 },
    attachTo: document.body,
    global: { stubs: { RouterLink: RouterLinkStub } },
  })
  await flushPromises()
  return modal
}

beforeEach(() => {
  logado.value = false
  obterVotacao.mockReset()
  document.body.innerHTML = ''
})

describe('VotacaoModal', () => {
  it('mostra o placar da votação nominal', async () => {
    await abrir({})

    expect(obterVotacao).toHaveBeenCalledWith(1)
    expect(document.body.textContent).toContain('PLP 299/2026')
    expect(document.body.textContent).toContain('45 (59%)')
  })

  it('explica que a votação simbólica não tem voto individual', async () => {
    await abrir({ nominal: false, placar: {} })

    expect(document.body.textContent).toContain('Votação simbólica')
    expect(document.body.textContent).not.toContain('Parlamentares que você segue')
  })

  it('pede login para ver os votos de quem o usuário segue', async () => {
    await abrir({})

    expect(document.body.textContent).toContain('para ver como os parlamentares que você segue votaram')
  })

  it('lista o voto dos parlamentares seguidos quando está logado', async () => {
    logado.value = true
    await abrir({ votos_seguidos: [{ id: 7, nome: 'Ana Lima', partido: 'PT', estado: 'ES', voto: 'Sim' }] })

    expect(document.body.textContent).toContain('Ana Lima (PT/ES)')
    expect(document.body.textContent).toContain('Sim')
  })

  it('mostra o erro e permite tentar de novo quando a busca falha', async () => {
    obterVotacao.mockRejectedValue(new Error('Câmara fora do ar'))
    mount(VotacaoModal, { props: { votacaoId: 1 }, attachTo: document.body })
    await flushPromises()

    expect(document.body.textContent).toContain('Câmara fora do ar')
  })

  it('emite fechar ao apertar Esc', async () => {
    const modal = await abrir({})

    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))

    expect(modal.emitted('fechar')).toHaveLength(1)
  })
})
