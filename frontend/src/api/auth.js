import { get, post } from './http'

export const registrar = (dados) => post('/api/auth/registro', dados)
export const entrar = (dados) => post('/api/auth/login', dados)
export const sair = () => post('/api/auth/logout')
export const obterUsuario = () => get('/api/auth/me')
