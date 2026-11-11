import { afterEach, describe, expect, it, vi } from 'vitest'
import { ErroApi, comParametros, get, post } from '../src/api/http'

function respostaFalsa(status, corpo) {
  return { ok: status < 400, status, json: async () => corpo }
}

afterEach(() => vi.unstubAllGlobals())

describe('comParametros', () => {
  it('omite valores vazios e falsos', () => {
    const url = comParametros('/api/x', { data: '2026-11-11', busca: '', ativo: false, pagina: 2 })
    expect(url).toBe('/api/x?data=2026-11-11&pagina=2')
  })

  it('retorna a url pura sem parâmetros', () => {
    expect(comParametros('/api/x', { a: '' })).toBe('/api/x')
  })
})

describe('requisições', () => {
  it('devolve o JSON em caso de sucesso', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respostaFalsa(200, { ok: true })))
    expect(await get('/api/x')).toEqual({ ok: true })
  })

  it('retorna null em 204', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respostaFalsa(204)))
    expect(await post('/api/auth/logout')).toBeNull()
  })

  it('lança ErroApi com mensagem e detalhes do servidor', async () => {
    const corpo = { erro: 'Dados inválidos.', detalhes: { email: 'E-mail inválido.' } }
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(respostaFalsa(422, corpo)))

    const erro = await post('/api/auth/login', {}).catch((e) => e)

    expect(erro).toBeInstanceOf(ErroApi)
    expect(erro.status).toBe(422)
    expect(erro.detalhes.email).toBe('E-mail inválido.')
  })

  it('traduz falha de rede para mensagem amigável', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('failed')))

    const erro = await get('/api/x').catch((e) => e)

    expect(erro.message).toBe('Não foi possível conectar ao servidor.')
    expect(erro.status).toBe(0)
  })
})
