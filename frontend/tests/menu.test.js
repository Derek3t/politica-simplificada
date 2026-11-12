import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'
import SidebarMenu from '../src/components/SidebarMenu.vue'

const rotas = ['/agenda', '/calendario', '/votacoes', '/parlamentares', '/busca', '/login']

async function montar() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: rotas.map((path) => ({ path, component: { template: '<div />' } })),
  })
  router.push('/agenda')
  await router.isReady()
  return mount(SidebarMenu, { global: { plugins: [router] } })
}

describe('SidebarMenu', () => {
  it('lista as telas do app, sem item Início', async () => {
    const menu = await montar()
    const nomes = menu.findAll('aside nav a').map((link) => link.text())

    expect(nomes).toEqual(['Agenda', 'Calendário', 'Votações', 'Parlamentares', 'Busca'])
  })

  it('o logo leva para a agenda e não para a tela de boas-vindas', async () => {
    const menu = await montar()

    expect(menu.find('aside a').attributes('href')).toBe('/agenda')
    expect(menu.find('header a').attributes('href')).toBe('/agenda')
  })

  it('a barra inferior do celular tem os mesmos destinos e rótulo curto para Parlamentares', async () => {
    const menu = await montar()
    const links = menu.findAll('nav.fixed a')

    expect(links.map((link) => link.attributes('href'))).toEqual([
      '/agenda',
      '/calendario',
      '/votacoes',
      '/parlamentares',
      '/busca',
    ])
    expect(links[3].text()).toBe('Deputados')
  })

  it('destaca apenas o item da rota atual', async () => {
    const menu = await montar()
    const ativos = menu.findAll('aside nav a').filter((link) => link.classes().includes('!bg-primaria'))

    expect(ativos.map((link) => link.text())).toEqual(['Agenda'])
  })
})
