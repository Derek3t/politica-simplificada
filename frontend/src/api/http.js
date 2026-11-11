export class ErroApi extends Error {
  constructor(mensagem, status, detalhes = null) {
    super(mensagem)
    this.status = status
    this.detalhes = detalhes
  }
}

async function requisitar(metodo, url, corpo) {
  let resposta
  try {
    resposta = await fetch(url, {
      method: metodo,
      headers: corpo ? { 'Content-Type': 'application/json' } : undefined,
      body: corpo ? JSON.stringify(corpo) : undefined,
    })
  } catch {
    throw new ErroApi('Não foi possível conectar ao servidor.', 0)
  }

  if (resposta.status === 204) return null

  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    throw new ErroApi(dados.erro ?? 'Erro inesperado.', resposta.status, dados.detalhes)
  }
  return dados
}

export const get = (url) => requisitar('GET', url)
export const post = (url, corpo) => requisitar('POST', url, corpo ?? {})
export const del = (url) => requisitar('DELETE', url)

export function comParametros(url, parametros) {
  const busca = new URLSearchParams()
  for (const [chave, valor] of Object.entries(parametros)) {
    if (valor !== '' && valor !== null && valor !== undefined && valor !== false) busca.set(chave, valor)
  }
  const texto = busca.toString()
  return texto ? `${url}?${texto}` : url
}
