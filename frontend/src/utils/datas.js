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

const formatoMes = new Intl.DateTimeFormat('pt-BR', { month: 'long', year: 'numeric' })

export const mesDe = (iso) => iso.slice(0, 7)

export const ehMesValido = (mes) => /^\d{4}-(0[1-9]|1[0-2])$/.test(mes ?? '')

export function somarMeses(mes, quantidade) {
  const [ano, numero] = mes.split('-').map(Number)
  return mesDe(paraISO(new Date(ano, numero - 1 + quantidade, 1)))
}

export function formatarMes(mes) {
  const texto = formatoMes.format(paraData(`${mes}-01`))
  return texto.charAt(0).toUpperCase() + texto.slice(1)
}

export function diasDoCalendario(mes) {
  const [ano, numero] = mes.split('-').map(Number)
  const vazios = new Date(ano, numero - 1, 1).getDay()
  const total = new Date(ano, numero, 0).getDate()
  const dias = Array.from({ length: total }, (_, i) => `${mes}-${String(i + 1).padStart(2, '0')}`)
  return [...Array(vazios).fill(null), ...dias]
}
