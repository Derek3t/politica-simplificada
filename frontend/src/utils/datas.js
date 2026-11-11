const formatoLongo = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  year: 'numeric',
})
const formatoDiaSemana = new Intl.DateTimeFormat('pt-BR', { weekday: 'short' })
const formatoDiaMes = new Intl.DateTimeFormat('pt-BR', { day: 'numeric', month: 'short' })

function paraData(iso) {
  return new Date(`${iso}T12:00:00`)
}

export function paraISO(data) {
  const mes = String(data.getMonth() + 1).padStart(2, '0')
  const dia = String(data.getDate()).padStart(2, '0')
  return `${data.getFullYear()}-${mes}-${dia}`
}

export const hoje = () => paraISO(new Date())

export function somarDias(iso, dias) {
  const data = paraData(iso)
  data.setDate(data.getDate() + dias)
  return paraISO(data)
}

export const ehDataValida = (iso) => /^\d{4}-\d{2}-\d{2}$/.test(iso ?? '') && !Number.isNaN(paraData(iso).getTime())

export function formatarLonga(iso) {
  const texto = formatoLongo.format(paraData(iso))
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

export const formatarDiaSemana = (iso) => formatoDiaSemana.format(paraData(iso)).replace('.', '')
export const formatarDiaMes = (iso) => formatoDiaMes.format(paraData(iso)).replace('.', '')
