<script setup>
import Icone from '../components/Icone.vue'
</script>

<template>
  <div class="flex min-h-screen flex-col bg-marinho text-white">
    <header class="flex items-center justify-between px-6 py-5">
      <span class="flex items-center gap-2 font-semibold"><Icone nome="marca" :tamanho="26" /> Política Simplificada</span>
      <RouterLink to="/login" class="text-sm text-slate-300 hover:text-white">Entrar</RouterLink>
    </header>

    <main class="mx-auto flex w-full max-w-3xl flex-1 flex-col items-center justify-center px-6 text-center">
      <h1 class="text-4xl font-bold leading-tight sm:text-5xl">Entenda hoje o que importa para o Brasil.</h1>
      <p class="mt-5 max-w-xl text-lg text-slate-300">
        Votações, projetos de lei, feriados e datas históricas explicados de forma simples e direta.
      </p>
      <RouterLink
        to="/agenda"
        class="mt-8 rounded-xl border border-white/40 px-6 py-3 font-medium transition hover:bg-white hover:text-marinho"
      >
        Começar agora →
      </RouterLink>
    </main>

    <footer class="py-6 text-center text-sm text-slate-400">Informação é cidadania.</footer>
  </div>
</template>
