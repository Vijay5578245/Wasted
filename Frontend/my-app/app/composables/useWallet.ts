interface WalletData {
  rate_per_minute: number
  total_wasted: number
  last_updated: string
}

export const useWallet = () => {
  const config = useRuntimeConfig()
  const API = config.public.apiBase as string
  const { token, isLoggedIn } = useAuth()

  const ratePerMin = useState<number>('wallet_rate', () => 0)
  const displayAmount = useState<number>('wallet_display', () => 0)
  const walletReady = useState<boolean>('wallet_ready', () => false)

  // ms-level rate for the 100ms tick
  const ratePerMs = computed(() => ratePerMin.value / 60000)

  let tickTimer: ReturnType<typeof setInterval> | null = null
  let syncTimer: ReturnType<typeof setInterval> | null = null

  async function fetchWallet() {
    if (!token.value) return
    try {
      const data = await $fetch<WalletData>(`${API}/wallet`, {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      // Compute catch-up: money that accumulated while away
      const raw = data.last_updated
      const isoStr = raw.endsWith('Z') || raw.includes('+') ? raw : raw + 'Z'
      const lastUpdated = new Date(isoStr)
      const minutesElapsed = Math.max(0, (Date.now() - lastUpdated.getTime()) / 60000)
      displayAmount.value = data.total_wasted + data.rate_per_minute * minutesElapsed
      ratePerMin.value = data.rate_per_minute
      walletReady.value = true
    } catch (e) {
      console.error('wallet fetch failed:', e)
    }
  }

  async function syncWallet() {
    if (!token.value) return
    try {
      await $fetch(`${API}/wallet`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token.value}` },
        body: {
          total_wasted: displayAmount.value,
          rate_per_minute: ratePerMin.value,
        },
      })
    } catch (e) {
      console.error('wallet sync failed:', e)
    }
  }

  async function setRate(newRate: number) {
    // Sync current total before changing rate so catch-up calculation stays accurate
    if (isLoggedIn.value) await syncWallet()
    ratePerMin.value = newRate
    if (isLoggedIn.value) await syncWallet()
  }

  function startTicking() {
    if (tickTimer) clearInterval(tickTimer)
    tickTimer = setInterval(() => {
      if (ratePerMin.value > 0) {
        displayAmount.value += ratePerMs.value * 100
      }
    }, 100)
  }

  function startSyncing() {
    if (syncTimer) clearInterval(syncTimer)
    syncTimer = setInterval(() => {
      if (isLoggedIn.value) syncWallet()
    }, 300_000)
  }

  function stopAll() {
    if (tickTimer) { clearInterval(tickTimer); tickTimer = null }
    if (syncTimer) { clearInterval(syncTimer); syncTimer = null }
  }

  return {
    ratePerMin,
    displayAmount,
    walletReady,
    fetchWallet,
    syncWallet,
    setRate,
    startTicking,
    startSyncing,
    stopAll,
  }
}
