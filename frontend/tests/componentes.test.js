import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import DayStrip from '../src/components/DayStrip.vue'
import FormCampo from '../src/components/FormCampo.vue'
import Paginacao from '../src/components/Paginacao.vue'
import ParlamentarCard from '../src/components/ParlamentarCard.vue'

describe('FormCampo', () => {
  it('atualiza o v-model ao digitar', async () => {
    const campo = mount(FormCampo, {
      props: { rotulo: 'E-mail', modelValue: '', 'onUpdate:modelValue': (v) => campo.setProps({ modelValue: v }) },
    })

    await campo.find('input').setValue('ana@exemplo.com')

    expect(campo.props('modelValue')).toBe('ana@exemplo.com')
  })

  it('exibe a mensagem de erro e marca o campo como inválido', () => {
    const campo = mount(FormCampo, { props: { rotulo: 'Senha', modelValue: '', erro: 'Informe a senha.' } })

    expect(campo.text()).toContain('Informe a senha.')
    expect(campo.find('input').attributes('aria-invalid')).toBe('true')
  })
})

describe('DayStrip', () => {
  it('mostra sete dias e emite o dia clicado', async () => {
    const faixa = mount(DayStrip, { props: { data: '2026-11-11' } })
    const botoes = faixa.findAll('button')

    expect(botoes).toHaveLength(7)
    expect(botoes[3].attributes('aria-selected')).toBe('true')

    await botoes[4].trigger('click')

    expect(faixa.emitted('selecionar')[0]).toEqual(['2026-11-12'])
  })
})

describe('ParlamentarCard', () => {
  const parlamentar = { id: 1, nome: 'Maria Souza', partido: 'PT', estado: 'ES', foto_link: null, seguido: false }

  it('mostra Seguir e emite o evento ao clicar', async () => {
    const card = mount(ParlamentarCard, { props: { parlamentar } })

    expect(card.text()).toContain('PT/ES')
    await card.find('button').trigger('click')

    expect(card.emitted('alternar-seguir')[0]).toEqual([parlamentar])
  })

  it('mostra Seguindo quando já segue', () => {
    const card = mount(ParlamentarCard, { props: { parlamentar: { ...parlamentar, seguido: true } } })

    expect(card.find('button').text()).toBe('Seguindo')
  })
})

describe('Paginacao', () => {
  it('não aparece com uma única página', () => {
    const paginacao = mount(Paginacao, { props: { pagina: 1, totalPaginas: 1 } })

    expect(paginacao.find('nav').exists()).toBe(false)
  })

  it('emite a página anterior e a próxima e bloqueia os extremos', async () => {
    const paginacao = mount(Paginacao, { props: { pagina: 2, totalPaginas: 3 } })
    const [anterior, proxima] = paginacao.findAll('button')

    await anterior.trigger('click')
    await proxima.trigger('click')

    expect(paginacao.emitted('mudar')).toEqual([[1], [3]])

    await paginacao.setProps({ pagina: 3 })
    expect(paginacao.findAll('button')[1].attributes('disabled')).toBeDefined()
  })
})
