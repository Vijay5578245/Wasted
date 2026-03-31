<template>
  <div class="relative w-screen h-screen overflow-hidden" style="background-color: #07050f;">

    <!-- Background orbs -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
      <div
        class="orb-animate absolute rounded-full"
        style="
          width: 65vw; height: 65vw;
          top: -25%; left: -15%;
          background: radial-gradient(circle, rgba(74,14,130,0.14) 0%, transparent 65%);
          filter: blur(4px);
        "
      />
      <div
        class="orb-animate absolute rounded-full"
        style="
          width: 50vw; height: 50vw;
          bottom: -20%; right: -10%;
          background: radial-gradient(circle, rgba(55,10,100,0.10) 0%, transparent 65%);
          filter: blur(6px);
          animation-delay: -9s;
        "
      />
      <!-- Fine noise grain via SVG filter -->
      <svg class="absolute inset-0 w-full h-full opacity-[0.025]" xmlns="http://www.w3.org/2000/svg">
        <filter id="noise">
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#noise)" />
      </svg>
    </div>

    <!-- ─── Verification banner ──────────────────────────── -->
    <Transition name="fade">
      <div
        v-if="isLoggedIn && !isVerified"
        class="absolute top-0 left-0 right-0 z-20 flex items-center justify-center gap-3
               py-2 bg-void-950/80 border-b border-void-900/40 backdrop-blur-sm"
      >
        <span class="text-[9px] uppercase tracking-ultra font-inter text-void-600">
          verify your email to secure your account
        </span>
        <span class="text-void-800">·</span>
        <span class="text-[9px] uppercase tracking-ultra font-inter text-void-700">
          {{ user?.email }}
        </span>
      </div>
    </Transition>

    <!-- ─── Header ─────────────────────────────────────────── -->
    <header class="absolute top-0 left-0 right-0 h-16 flex items-center justify-between px-8 z-10"
            :style="isLoggedIn && !isVerified ? 'top: 2rem' : ''">
      <!-- Brand -->
      <span
        class="font-cormorant font-light text-ink-200/60 tracking-ultra select-none"
        style="font-size: 0.875rem; letter-spacing: 0.35em;"
      >
        W A S T E D
      </span>

      <!-- Auth area -->
      <div class="flex items-center gap-4">
        <template v-if="isLoggedIn">
          <span class="text-[10px] uppercase tracking-ultra font-inter text-void-500">
            {{ user?.username }}
          </span>
          <button
            @click="handleLogout"
            class="text-[10px] uppercase tracking-ultra font-inter text-void-800
                   hover:text-void-500 transition-colors duration-200"
          >
            leave
          </button>
        </template>
        <template v-else>
          <button
            @click="showAuth = true"
            class="text-[10px] uppercase tracking-ultra font-inter text-void-600
                   hover:text-void-300 transition-colors duration-200
                   border-b border-void-900/0 hover:border-void-700/50 pb-0.5"
          >
            sign in
          </button>
        </template>
      </div>
    </header>

    <!-- ─── Main content ──────────────────────────────────── -->
    <main class="absolute inset-0 flex flex-col items-center justify-center gap-10">

      <!-- Money counter -->
      <MoneyCounter :amount="displayAmount" />

      <!-- Separator -->
      <div class="w-px h-6 bg-gradient-to-b from-void-900/80 to-transparent" />

      <!-- Rate input section -->
      <div class="flex flex-col items-center gap-4">
        <p class="text-[9px] uppercase tracking-ultra font-inter text-void-700 font-medium">
          rate of waste
        </p>

        <div class="flex items-baseline gap-2">
          <span class="font-cormorant font-light text-void-500/60"
                style="font-size: 1.5rem;">$</span>

          <input
            v-model="rateInput"
            type="number"
            step="0.01"
            min="0"
            placeholder="0.00"
            @keyup.enter="commitRate"
            @blur="commitRate"
            class="bg-transparent border-b-2 border-void-900/50
                   focus:border-void-600/60 text-ink-100 font-cormorant font-light
                   text-center outline-none placeholder-ink-900/60 transition-all duration-300
                   caret-void-400 w-36"
            style="font-size: 2rem; padding-bottom: 4px;"
          />

          <span class="text-[11px] tracking-ultra font-inter text-void-600/60 ml-1">/ min</span>
        </div>

        <!-- Rate active indicator -->
        <Transition name="fade">
          <div v-if="ratePerMin > 0" class="flex items-center gap-2 mt-1">
            <span
              class="inline-block w-1.5 h-1.5 rounded-full bg-void-600 opacity-80"
              style="box-shadow: 0 0 6px rgba(107,31,208,0.8); animation: glow-pulse 2s ease-in-out infinite;"
            />
            <span class="text-[9px] uppercase tracking-ultra font-inter text-void-700">
              draining
            </span>
          </div>
        </Transition>
      </div>

      <!-- Bottom quote -->
      <div class="absolute bottom-10 left-0 right-0 flex flex-col items-center gap-2">
        <div class="w-16 h-px bg-gradient-to-r from-transparent via-void-900/60 to-transparent" />
        <p class="font-cormorant font-light italic text-void-700/70 text-center"
           style="font-size: 0.875rem; letter-spacing: 0.04em;">
          every second, it slips further away
        </p>
      </div>

      <!-- Guest notice -->
      <Transition name="fade">
        <div
          v-if="!isLoggedIn && ratePerMin > 0"
          class="absolute bottom-28 left-0 right-0 flex justify-center"
        >
          <button
            @click="showAuth = true"
            class="text-[9px] uppercase tracking-ultra font-inter text-void-800
                   hover:text-void-500 transition-colors duration-200 border-b border-void-900/0
                   hover:border-void-800/50 pb-0.5"
          >
            sign in to preserve your waste
          </button>
        </div>
      </Transition>
    </main>

    <!-- ─── Intro overlay ─────────────────────────────────── -->
    <IntroOverlay />

    <!-- ─── Auth modal ────────────────────────────────────── -->
    <AuthModal
      :open="showAuth"
      @close="showAuth = false"
      @authenticated="onAuthenticated"
    />
  </div>
</template>

<script setup lang="ts">
const { user, isLoggedIn, isVerified, token, fetchUser, logout } = useAuth()
const { ratePerMin, displayAmount, fetchWallet, setRate, startTicking, startSyncing, stopAll, syncWallet } = useWallet()

const showAuth = ref(false)
const rateInput = ref<string>('')

async function commitRate() {
  const val = parseFloat(rateInput.value)
  if (isNaN(val) || val < 0) return
  await setRate(val)
}

async function onAuthenticated() {
  stopAll()
  await fetchWallet()
  // Seed the rate input from saved wallet
  if (ratePerMin.value > 0) {
    rateInput.value = ratePerMin.value.toString()
  }
  startTicking()
  startSyncing()
}

async function handleLogout() {
  if (isLoggedIn.value) await syncWallet()
  stopAll()
  logout()
  // Reset local state
  displayAmount.value = 0
  ratePerMin.value = 0
  rateInput.value = ''
  startTicking()
}

onMounted(async () => {
  // Restore auth session
  await fetchUser()

  if (isLoggedIn.value) {
    await fetchWallet()
    if (ratePerMin.value > 0) {
      rateInput.value = ratePerMin.value.toString()
    }
  }

  startTicking()
  startSyncing()

  // Capture apiBase once here — Nuxt composables can't be called inside event listeners
  const apiBase = useRuntimeConfig().public.apiBase as string

  // Recalculate catch-up the instant the user returns to the tab
  let hiddenAt: number | null = null
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      hiddenAt = Date.now()
    } else if (hiddenAt !== null && ratePerMin.value > 0) {
      const minutesAway = (Date.now() - hiddenAt) / 60000
      displayAmount.value += ratePerMin.value * minutesAway
      hiddenAt = null
    }
  })

  // Best-effort sync on tab close
  window.addEventListener('beforeunload', () => {
    if (!isLoggedIn.value || !token.value) return
    fetch(`${apiBase}/wallet`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token.value}`,
      },
      body: JSON.stringify({
        total_wasted: displayAmount.value,
        rate_per_minute: ratePerMin.value,
      }),
      keepalive: true,
    }).catch(() => {})
  })
})

onUnmounted(() => {
  stopAll()
})
</script>
