import type { Ref } from 'vue'

/** Copie de `source` qui n'adopte sa valeur qu'une fois la frappe calmée. */
export function useDebounced<T>(source: Ref<T>, delayMs: number): Ref<T> {
  const settled = ref(source.value) as Ref<T>
  let timer: ReturnType<typeof setTimeout> | undefined

  watch(source, (value) => {
    clearTimeout(timer)
    timer = setTimeout(() => {
      settled.value = value
    }, delayMs)
  })

  onBeforeUnmount(() => clearTimeout(timer))

  return settled
}
