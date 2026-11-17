const ESTILOS = {
  Sim: 'bg-emerald-100 text-emerald-700',
  Não: 'bg-red-100 text-red-700',
  Abstenção: 'bg-amber-100 text-amber-700',
}

export const estiloVoto = (voto) => ESTILOS[voto] ?? 'bg-slate-100 text-slate-600'

export function porcentagens(contagem) {
  const total = Object.values(contagem).reduce((soma, n) => soma + n, 0)
  return Object.entries(contagem).map(([voto, quantidade]) => ({
    voto,
    quantidade,
    percentual: total ? Math.round((quantidade / total) * 100) : 0,
  }))
}
