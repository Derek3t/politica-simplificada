<script setup>
defineProps({
  parlamentar: { type: Object, required: true },
  posicionamento: { type: String, default: '' },
  ocupado: { type: Boolean, default: false },
})
defineEmits(['alternar-seguir'])
</script>

<template>
  <li class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white p-3">
    <img
      v-if="parlamentar.foto_link"
      :src="parlamentar.foto_link"
      :alt="`Foto de ${parlamentar.nome}`"
      loading="lazy"
      class="h-12 w-12 rounded-full bg-slate-100 object-cover"
    />
    <span v-else class="h-12 w-12 rounded-full bg-slate-200" />
    <div class="min-w-0 flex-1">
      <RouterLink
        :to="{ name: 'parlamentar', params: { id: parlamentar.id } }"
        class="block truncate font-medium text-slate-900 hover:text-primaria hover:underline"
      >
        {{ parlamentar.nome }}
      </RouterLink>
      <p class="text-sm text-slate-500">
        {{ parlamentar.partido }}/{{ parlamentar.estado }}
        <span class="ml-1 text-xs text-slate-400">{{ parlamentar.casa === 'Senado' ? 'Senador(a)' : 'Deputado(a)' }}</span>
        <span v-if="posicionamento" class="ml-1 rounded bg-slate-100 px-1.5 py-0.5 text-xs">{{ posicionamento }}</span>
      </p>
    </div>
    <button
      type="button"
      :disabled="ocupado"
      class="shrink-0 rounded-lg border px-3 py-1.5 text-sm font-medium transition disabled:opacity-50"
      :class="
        parlamentar.seguido
          ? 'border-primaria bg-primaria text-white'
          : 'border-slate-300 text-slate-700 hover:border-primaria hover:text-primaria'
      "
      @click="$emit('alternar-seguir', parlamentar)"
    >
      {{ parlamentar.seguido ? 'Seguindo' : 'Seguir' }}
    </button>
  </li>
</template>
