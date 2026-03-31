<template>
  <Transition name="intro">
    <div
      v-if="visible"
      class="fixed inset-0 z-[9000] flex items-center justify-center bg-black"
    >
      <!-- Subtle vignette at edges -->
      <div class="absolute inset-0 bg-radial-vignette pointer-events-none" />

      <div class="relative flex flex-col items-center gap-6 select-none">
        <h1
          class="font-cormorant font-light text-white tracking-extreme"
          style="font-size: clamp(3.5rem, 8vw, 7rem); letter-spacing: 0.55em;"
        >
          Wasted
        </h1>
        <div class="w-12 h-px bg-gradient-to-r from-transparent via-purple-600/50 to-transparent" />
      </div>
    </div>
  </Transition>
</template>

<script setup lang="ts">
const visible = ref(true)

onMounted(() => {
  setTimeout(() => {
    visible.value = false
  }, 700)
})
</script>

<style scoped>
.intro-leave-active {
  transition: opacity 1.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.intro-leave-to {
  opacity: 0;
}

.bg-radial-vignette {
  background: radial-gradient(
    ellipse 70% 70% at 50% 50%,
    transparent 40%,
    rgba(0, 0, 0, 0.7) 100%
  );
}
</style>
