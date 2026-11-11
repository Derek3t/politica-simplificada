import { describe, expect, it } from 'vitest'
import {
  diasDoCalendario,
  ehDataValida,
  ehMesValido,
  formatarLonga,
  formatarMes,
  paraISO,
  somarDias,
  somarMeses,
} from '../src/utils/datas'

describe('datas', () => {
  it('soma dias atravessando o mês e o ano', () => {
    expect(somarDias('2026-11-30', 1)).toBe('2026-12-01')
    expect(somarDias('2026-01-01', -1)).toBe('2025-12-31')
  })

  it('converte Date para ISO sem deslocar por fuso', () => {
    expect(paraISO(new Date(2026, 10, 5))).toBe('2026-11-05')
  })

  it('valida formato de data', () => {
    expect(ehDataValida('2026-11-11')).toBe(true)
    expect(ehDataValida('11/11/2026')).toBe(false)
    expect(ehDataValida(undefined)).toBe(false)
    expect(ehDataValida('2026-13-45')).toBe(false)
  })

  it('formata data longa em português com inicial maiúscula', () => {
    expect(formatarLonga('2026-11-11')).toBe('Quarta-feira, 11 de novembro de 2026')
  })
})

describe('calendário', () => {
  it('soma meses atravessando o ano', () => {
    expect(somarMeses('2026-12', 1)).toBe('2027-01')
    expect(somarMeses('2026-01', -1)).toBe('2025-12')
  })

  it('valida formato de mês', () => {
    expect(ehMesValido('2026-11')).toBe(true)
    expect(ehMesValido('2026-13')).toBe(false)
    expect(ehMesValido('novembro')).toBe(false)
  })

  it('monta a grade com espaços vazios antes do dia 1', () => {
    const dias = diasDoCalendario('2026-11')

    expect(dias).toHaveLength(30)
    expect(dias[0]).toBe('2026-11-01')
    expect(diasDoCalendario('2026-10').slice(0, 5)).toEqual([null, null, null, null, '2026-10-01'])
  })

  it('formata o mês por extenso', () => {
    expect(formatarMes('2026-11')).toBe('Novembro de 2026')
  })
})
