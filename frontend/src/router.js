import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from './composables/useAuth'
import AgendaView from './views/AgendaView.vue'
import BoasVindasView from './views/BoasVindasView.vue'
import LoginView from './views/LoginView.vue'
import ParlamentaresView from './views/ParlamentaresView.vue'
import VotacoesView from './views/VotacoesView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'inicio', component: BoasVindasView, meta: { semMenu: true } },
    { path: '/agenda', name: 'agenda', component: AgendaView },
    { path: '/votacoes', name: 'votacoes', component: VotacoesView },
    { path: '/parlamentares', name: 'parlamentares', component: ParlamentaresView },
    { path: '/login', name: 'login', component: LoginView, meta: { semMenu: true, visitante: true } },
    { path: '/cadastro', name: 'cadastro', component: LoginView, meta: { semMenu: true, visitante: true } },
    { path: '/:resto(.*)*', redirect: '/' },
  ],
})

router.beforeEach(async (destino) => {
  const { logado, carregarUsuario } = useAuth()
  await carregarUsuario()
  if (destino.meta.visitante && logado.value) return { name: 'agenda' }
})

export default router
