import { computed, ref } from 'vue'
import * as api from '../api/auth'

const usuario = ref(null)
const verificado = ref(false)

export function useAuth() {
  async function carregarUsuario() {
    if (verificado.value) return
    try {
      usuario.value = (await api.obterUsuario()).usuario
    } catch {
      usuario.value = null
    }
    verificado.value = true
  }

  async function entrar(dados) {
    usuario.value = (await api.entrar(dados)).usuario
  }

  async function cadastrar(dados) {
    usuario.value = (await api.registrar(dados)).usuario
  }

  async function sair() {
    await api.sair()
    usuario.value = null
  }

  return { usuario, logado: computed(() => usuario.value !== null), carregarUsuario, entrar, cadastrar, sair }
}
