<script setup>
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import Icone from './Icone.vue'

const router = useRouter()
const { usuario, logado, sair } = useAuth()

const itens = [
  { nome: 'Início', rota: '/', icone: 'inicio' },
  { nome: 'Busca', rota: '/busca', icone: 'busca' },
  { nome: 'Agenda', rota: '/agenda', icone: 'agenda' },
  { nome: 'Calendário', rota: '/calendario', icone: 'calendario' },
  { nome: 'Votações', rota: '/votacoes', icone: 'votacoes' },
  { nome: 'Parlamentares', curto: 'Deputados', rota: '/parlamentares', icone: 'parlamentares' },
]

async function aoSair() {
  await sair()
  router.push('/')
}
</script>

<template>
  <aside class="hidden w-64 shrink-0 flex-col bg-marinho p-5 text-white md:sticky md:top-0 md:flex md:h-screen">
    <RouterLink to="/" class="flex items-center gap-3">
      <Icone nome="marca" :tamanho="32" />
      <span class="text-lg font-semibold leading-tight">Política<br />Simplificada</span>
    </RouterLink>
    <p class="mt-3 text-sm text-slate-300">Entenda hoje o que importa para o Brasil.</p>

    <nav class="mt-8 flex flex-col gap-1">
      <RouterLink
        v-for="item in itens"
        :key="item.rota"
        :to="item.rota"
        class="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-200 hover:bg-marinho-claro"
        active-class="!bg-primaria !text-white"
        :exact-active-class="item.rota === '/' ? '!bg-primaria !text-white' : ''"
      >
        <Icone :nome="item.icone" />
        {{ item.nome }}
      </RouterLink>
    </nav>

    <div class="mt-auto border-t border-white/10 pt-4 text-sm">
      <template v-if="logado">
        <p class="truncate font-medium">{{ usuario.nome }}</p>
        <p class="truncate text-xs text-slate-400">{{ usuario.email }}</p>
        <button type="button" class="mt-3 flex items-center gap-2 text-slate-300 hover:text-white" @click="aoSair">
          <Icone nome="sair" :tamanho="16" /> Sair
        </button>
      </template>
      <RouterLink v-else to="/login" class="block rounded-lg bg-white/10 px-3 py-2 text-center hover:bg-white/20">
        Entrar
      </RouterLink>
    </div>
  </aside>

  <header class="flex items-center justify-between bg-marinho px-4 py-3 text-white md:hidden">
    <RouterLink to="/" class="flex items-center gap-2 font-semibold">
      <Icone nome="marca" :tamanho="22" /> Política Simplificada
    </RouterLink>
    <button v-if="logado" type="button" class="text-sm text-slate-300" @click="aoSair">Sair</button>
    <RouterLink v-else to="/login" class="text-sm text-slate-200">Entrar</RouterLink>
  </header>

  <nav class="fixed inset-x-0 bottom-0 z-40 flex justify-around border-t border-slate-200 bg-white py-2 md:hidden">
    <RouterLink
      v-for="item in itens"
      :key="item.rota"
      :to="item.rota"
      class="flex min-w-0 flex-1 flex-col items-center gap-0.5 px-0.5 text-[10px] text-slate-500"
      active-class="!text-primaria"
      :exact-active-class="item.rota === '/' ? '!text-primaria' : ''"
    >
      <Icone :nome="item.icone" :tamanho="22" />
      {{ item.curto ?? item.nome }}
    </RouterLink>
  </nav>
</template>
