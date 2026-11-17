import { ref, watch } from 'vue'

export const UFS = 'AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO'.split(' ')

const CHAVE = 'politica-uf'

function lerSalva() {
  try {
    const uf = localStorage.getItem(CHAVE)
    return UFS.includes(uf) ? uf : ''
  } catch {
    return ''
  }
}

const uf = ref(lerSalva())

watch(uf, (novo) => {
  try {
    localStorage.setItem(CHAVE, novo)
  } catch {
    // sem armazenamento (modo privado): a escolha vale só até recarregar
  }
})

export const useRegiao = () => ({ uf })
