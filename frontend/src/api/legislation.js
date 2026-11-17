import { comParametros, del, get, post } from './http'

const BASE = '/api/legislation'

export const obterAgenda = (data, { incluirComissoes, apenasSeguidos, uf }) =>
  get(
    comParametros(`${BASE}/agenda`, {
      data,
      incluir_comissoes: incluirComissoes,
      apenas_seguidos: apenasSeguidos,
      uf,
    }),
  )

export const buscar = (q) => get(comParametros(`${BASE}/busca`, { q }))

export const obterCalendario = (mes, uf) => get(comParametros(`${BASE}/calendario`, { mes, uf }))

export const obterProjeto = (id) => get(`${BASE}/projetos/${id}`)
export const analisarProjeto = (id) => post(`${BASE}/projetos/${id}/analisar`)
export const contextualizarDia = (id) => post(`${BASE}/dias-especiais/${id}/contextualizar`)

export const listarVotacoes = (filtros) => get(comParametros(`${BASE}/votacoes`, filtros))
export const obterVotacao = (id) => get(`${BASE}/votacoes/${id}`)

export const listarParlamentares = (filtros) => get(comParametros(`${BASE}/parlamentares`, filtros))
export const obterParlamentar = (id) => get(`${BASE}/parlamentares/${id}`)
export const listarSeguidos = () => get(`${BASE}/parlamentares/seguidos`)
export const seguirParlamentar = (id) => post(`${BASE}/parlamentares/${id}/seguir`)
export const deixarDeSeguir = (id) => del(`${BASE}/parlamentares/${id}/seguir`)

export const urlCalendario = (projetoId) => `/api/calendar/projetos/${projetoId}.ics`
export const adicionarAoGoogle = (projetoId) => post(`/api/calendar/projetos/${projetoId}/google`)
