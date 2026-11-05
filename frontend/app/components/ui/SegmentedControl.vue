<template>
  <div role="group" :aria-label="label" class="inline-flex flex-wrap gap-1 rounded-md bg-deep p-1">
    <button
      v-for="option in options"
      :key="option.value"
      type="button"
      class="min-h-11 rounded px-3 font-medium"
      :class="option.value === modelValue ? 'bg-hot text-deep' : 'text-soft hover:text-text'"
      :aria-pressed="option.value === modelValue"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.label }}
    </button>
  </div>
</template>

<script setup lang="ts" generic="T extends string">
import type { ChoiceOption } from '~/types'

defineProps<{ modelValue: T; options: ChoiceOption<T>[]; label: string }>()
defineEmits<{ 'update:modelValue': [value: T] }>()
</script>
