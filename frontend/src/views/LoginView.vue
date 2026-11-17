<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormCampo from '../components/FormCampo.vue'
import Icone from '../components/Icone.vue'
import { URL_LOGIN_GOOGLE } from '../api/auth'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { entrar, cadastrar } = useAuth()

const modoCadastro = computed(() => route.name === 'cadastro')
const campos = reactive({ nome: '', email: '', senha: '' })
const erros = reactive({ nome: '', email: '', senha: '' })
const erroGeral = ref(route.query.erro === 'google' ? 'Não foi possível entrar com o Google. Tente novamente.' : '')
const enviando = ref(false)

function validarLocalmente() {
  erros.nome = modoCadastro.value && campos.nome.trim().length < 2 ? 'Informe seu nome.' : ''
  erros.email = /^\S+@\S+\.\S+$/.test(campos.email.trim()) ? '' : 'E-mail inválido.'
  erros.senha =
    modoCadastro.value && campos.senha.length < 8 ? 'A senha deve ter no mínimo 8 caracteres.' : campos.senha ? '' : 'Informe a senha.'
  return !erros.nome && !erros.email && !erros.senha
}

async function enviar() {
  erroGeral.value = ''
  if (!validarLocalmente()) return

  enviando.value = true
  try {
    if (modoCadastro.value) await cadastrar({ ...campos })
    else await entrar({ email: campos.email, senha: campos.senha })
    router.push(route.query.redirect || '/agenda')
  } catch (e) {
    if (e.detalhes) Object.assign(erros, e.detalhes)
    else erroGeral.value = e.message
  } finally {
    enviando.value = false
  }
}
</script>

<template>
  <div class="flex min-h-screen items-center justify-center bg-marinho px-4">
    <div class="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">
      <RouterLink to="/" class="flex items-center gap-2 font-semibold text-marinho">
        <Icone nome="marca" :tamanho="24" /> Política Simplificada
      </RouterLink>
      <h1 class="mt-6 text-2xl font-bold text-slate-900">{{ modoCadastro ? 'Criar conta' : 'Entrar' }}</h1>

      <form class="mt-6 space-y-4" novalidate @submit.prevent="enviar">
        <FormCampo v-if="modoCadastro" v-model="campos.nome" rotulo="Nome" autocomplete="name" :erro="erros.nome" />
        <FormCampo v-model="campos.email" rotulo="E-mail" tipo="email" autocomplete="email" :erro="erros.email" />
        <FormCampo
          v-model="campos.senha"
          rotulo="Senha"
          tipo="password"
          :autocomplete="modoCadastro ? 'new-password' : 'current-password'"
          :erro="erros.senha"
        />

        <p v-if="erroGeral" class="text-sm text-red-600" role="alert">{{ erroGeral }}</p>

        <button
          type="submit"
          :disabled="enviando"
          class="w-full rounded-lg bg-primaria py-2.5 font-medium text-white disabled:opacity-60"
        >
          {{ enviando ? 'Aguarde…' : modoCadastro ? 'Criar conta' : 'Entrar' }}
        </button>
      </form>

      <div class="my-5 flex items-center gap-3 text-xs uppercase text-slate-400">
        <span class="h-px flex-1 bg-slate-200" /> ou <span class="h-px flex-1 bg-slate-200" />
      </div>
      <a
        :href="URL_LOGIN_GOOGLE"
        class="flex w-full items-center justify-center gap-3 rounded-lg border border-slate-300 py-2.5 font-medium text-slate-700 hover:bg-slate-50"
      >
        <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
          <path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.9 2.4 30.4 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.1C12.4 13.6 17.7 9.5 24 9.5z" />
          <path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.8c4.3-4 6.9-9.9 6.9-17.2z" />
          <path fill="#FBBC05" d="M10.5 28.7a14.5 14.5 0 0 1 0-9.4l-7.9-6.1a24 24 0 0 0 0 21.6l7.9-6.1z" />
          <path fill="#34A853" d="M24 48c6.5 0 11.9-2.1 15.9-5.8l-7.4-5.8c-2.1 1.4-4.8 2.3-8.5 2.3-6.3 0-11.6-4.1-13.5-9.8l-7.9 6.1C6.5 42.6 14.6 48 24 48z" />
        </svg>
        Continuar com o Google
      </a>

      <p class="mt-5 text-center text-sm text-slate-600">
        <template v-if="modoCadastro">
          Já tem conta?
          <RouterLink :to="{ name: 'login', query: route.query }" class="font-medium text-primaria">Entrar</RouterLink>
        </template>
        <template v-else>
          Não tem conta?
          <RouterLink :to="{ name: 'cadastro', query: route.query }" class="font-medium text-primaria">Cadastre-se</RouterLink>
        </template>
      </p>
    </div>
  </div>
</template>
