import { describe, expect, it } from 'vitest'
import { ehDataValida, formatarLonga, paraISO, somarDias } from '../src/utils/datas'

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
