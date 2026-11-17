import { describe, expect, it } from 'vitest'
import { estiloVoto, porcentagens } from '../src/utils/votos'

describe('votos', () => {
  it('calcula o percentual de cada voto', () => {
    expect(porcentagens({ Sim: 1, Não: 1, Abstenção: 2 })).toEqual([
      { voto: 'Sim', quantidade: 1, percentual: 25 },
      { voto: 'Não', quantidade: 1, percentual: 25 },
      { voto: 'Abstenção', quantidade: 2, percentual: 50 },
    ])
  })

  it('não divide por zero sem votos', () => {
    expect(porcentagens({})).toEqual([])
  })

  it('usa uma cor neutra para votos desconhecidos', () => {
    expect(estiloVoto('Sim')).toContain('emerald')
    expect(estiloVoto('Ausente')).toContain('slate')
  })
})
