<script setup>
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FormCampo from '../components/FormCampo.vue'
import Icone from '../components/Icone.vue'
import { useAuth } from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const { entrar, cadastrar } = useAuth()

const modoCadastro = computed(() => route.name === 'cadastro')
const campos = reactive({ nome: '', email: '', senha: '' })
const erros = reactive({ nome: '', email: '', senha: '' })
const erroGeral = ref('')
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
