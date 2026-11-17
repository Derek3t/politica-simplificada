import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { nextTick } from 'vue'

async function carregar() {
  vi.resetModules()
  return import('../src/composables/useRegiao')
}

function armazenamentoFalso(inicial = {}) {
  const dados = { ...inicial }
  return {
    getItem: (chave) => dados[chave] ?? null,
    setItem: (chave, valor) => {
      dados[chave] = valor
    },
  }
}

describe('useRegiao', () => {
  beforeEach(() => vi.stubGlobal('localStorage', armazenamentoFalso()))
  afterEach(() => vi.unstubAllGlobals())

  it('começa sem estado escolhido', async () => {
    const { useRegiao } = await carregar()

    expect(useRegiao().uf.value).toBe('')
  })

  it('guarda a escolha e a recupera ao recarregar', async () => {
    const { useRegiao } = await carregar()
    useRegiao().uf.value = 'ES'
    await nextTick()

    const recarregado = await carregar()

    expect(recarregado.useRegiao().uf.value).toBe('ES')
  })

  it('ignora um valor salvo que não é um estado', async () => {
    vi.stubGlobal('localStorage', armazenamentoFalso({ 'politica-uf': 'XX' }))
    const { useRegiao } = await carregar()

    expect(useRegiao().uf.value).toBe('')
  })
})
