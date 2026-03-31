<template>
  <div class="w-screen h-screen flex items-center justify-center" style="background-color: #07050f;">
    <div class="flex flex-col items-center gap-6 px-8 text-center max-w-sm">

      <!-- Loading -->
      <template v-if="status === 'loading'">
        <p class="text-[10px] uppercase tracking-ultra font-inter text-void-700">verifying</p>
      </template>

      <!-- Success -->
      <template v-else-if="status === 'success'">
        <h1 class="font-cormorant font-light text-ink-50 tracking-ultra"
            style="font-size: clamp(2.5rem, 6vw, 4rem);">
          Verified
        </h1>
        <div class="w-12 h-px bg-gradient-to-r from-transparent via-void-600/60 to-transparent" />
        <p class="text-void-500/80 font-inter text-xs tracking-wide">
          Your email has been confirmed.
        </p>
        <NuxtLink
          to="/"
          class="text-[10px] uppercase tracking-ultra font-inter text-void-400
                 hover:text-void-200 transition-colors border-b border-void-800/0
                 hover:border-void-700/50 pb-0.5"
        >
          return
        </NuxtLink>
      </template>

      <!-- Error -->
      <template v-else>
        <p class="font-cormorant font-light italic text-void-600/70"
           style="font-size: 1.5rem;">
          {{ error }}
        </p>
        <NuxtLink
          to="/"
          class="text-[10px] uppercase tracking-ultra font-inter text-void-700
                 hover:text-void-400 transition-colors"
        >
          go back
        </NuxtLink>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const config = useRuntimeConfig()
const { fetchUser } = useAuth()

const status = ref<'loading' | 'success' | 'error'>('loading')
const error = ref('Invalid or expired link')

onMounted(async () => {
  const token = route.query.token as string
  if (!token) {
    status.value = 'error'
    return
  }
  try {
    await $fetch(`${config.public.apiBase}/auth/verify/${token}`)
    await fetchUser() // refresh is_verified in state
    status.value = 'success'
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Verification failed'
    status.value = 'error'
  }
})
</script>
