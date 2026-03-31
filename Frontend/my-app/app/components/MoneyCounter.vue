<template>
  <div class="flex flex-col items-center gap-3 select-none">
    <!-- Eyebrow label -->
    <p class="text-[9px] uppercase tracking-ultra font-inter text-void-700 font-medium">
      you have wasted
    </p>

    <!-- The main counter -->
    <div
      class="counter-glow flex items-start justify-center font-cormorant font-light text-ink-50"
      style="font-size: clamp(4rem, 8.5vw, 8rem); line-height: 1; letter-spacing: -0.02em;"
    >
      <!-- Dollar sign -->
      <span
        class="font-cormorant font-light text-void-400/70"
        style="font-size: clamp(1.8rem, 3.5vw, 3.2rem); margin-top: 0.35em; margin-right: 0.15em;"
      >$</span>

      <!-- Integer part -->
      <span class="tabular-nums">{{ integerFormatted }}</span>

      <!-- Decimal part -->
      <span
        class="font-cormorant font-light text-ink-50/40 tabular-nums"
        style="font-size: clamp(2rem, 4vw, 3.6rem); align-self: flex-end; margin-bottom: 0.12em; margin-left: 0.05em;"
      >.{{ decimalFormatted }}</span>
    </div>

    <!-- Divider label -->
    <div class="flex items-center gap-3 mt-1">
      <div class="w-8 h-px bg-gradient-to-r from-transparent to-void-800/60" />
      <p class="text-[9px] uppercase tracking-ultra font-inter text-void-800 font-medium">
        this far
      </p>
      <div class="w-8 h-px bg-gradient-to-l from-transparent to-void-800/60" />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ amount: number }>()

const integerFormatted = computed(() => {
  const int = Math.floor(props.amount)
  return int.toLocaleString('en-US')
})

const decimalFormatted = computed(() => {
  const dec = Math.floor((props.amount % 1) * 100)
  return dec.toString().padStart(2, '0')
})
</script>
