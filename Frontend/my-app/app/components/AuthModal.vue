<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="props.open"
        class="fixed inset-0 z-[500] flex items-center justify-center px-4"
      >
        <!-- Backdrop -->
        <div
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="$emit('close')"
        />

        <!-- Card -->
        <div
          class="relative w-full max-w-[22rem] bg-ink-900 border border-void-900/40 rounded-lg p-8
                 shadow-[0_0_80px_rgba(107,31,208,0.12)]"
        >
          <div class="absolute -top-px left-1/2 -translate-x-1/2 w-24 h-px
                      bg-gradient-to-r from-transparent via-void-600/60 to-transparent" />

          <!-- Tab switcher -->
          <div class="flex gap-6 mb-8">
            <button
              v-for="tab in (['login', 'register'] as const)"
              :key="tab"
              @click="switchTab(tab)"
              class="text-[10px] uppercase tracking-ultra font-inter font-medium transition-colors duration-200"
              :class="activeTab === tab ? 'text-void-300' : 'text-void-800 hover:text-void-600'"
            >
              {{ tab }}
            </button>
          </div>

          <form @submit.prevent="handleSubmit" class="flex flex-col gap-4">

            <!-- Username -->
            <div class="flex flex-col gap-1">
              <label class="text-[9px] uppercase tracking-ultra text-void-700 font-inter">
                username
              </label>
              <input
                v-model="username"
                type="text"
                autocomplete="username"
                required
                class="bg-transparent pb-2 outline-none text-ink-100 text-sm font-inter font-light
                       placeholder-void-900 transition-colors duration-200 caret-void-400"
                :class="fieldErrors.username
                  ? 'border-b border-red-500/60'
                  : 'border-b border-void-900/60 focus:border-void-600/70'"
                placeholder="—"
              />
              <Transition name="fade">
                <p v-if="fieldErrors.username" class="text-red-400/70 text-[10px] font-inter mt-0.5">
                  {{ fieldErrors.username }}
                </p>
              </Transition>
            </div>

            <!-- Password -->
            <div class="flex flex-col gap-1">
              <label class="text-[9px] uppercase tracking-ultra text-void-700 font-inter">
                password
              </label>
              <input
                v-model="password"
                type="password"
                autocomplete="current-password"
                required
                class="bg-transparent pb-2 outline-none text-ink-100 text-sm font-inter font-light
                       placeholder-void-900 transition-colors duration-200 caret-void-400"
                :class="fieldErrors.password
                  ? 'border-b border-red-500/60'
                  : 'border-b border-void-900/60 focus:border-void-600/70'"
                placeholder="—"
              />
              <Transition name="fade">
                <p v-if="fieldErrors.password" class="text-red-400/70 text-[10px] font-inter mt-0.5">
                  {{ fieldErrors.password }}
                </p>
              </Transition>
              <p v-if="activeTab === 'register'" class="text-void-800/70 text-[9px] font-inter mt-1">
                Min 8 chars · letters, numbers, symbols
              </p>
            </div>

            <!-- General error -->
            <Transition name="fade">
              <p v-if="authError" class="text-red-400/70 text-xs font-inter">
                {{ authError }}
              </p>
            </Transition>

            <button
              type="submit"
              :disabled="authLoading"
              class="mt-2 py-2.5 text-[10px] uppercase tracking-ultra font-inter font-medium
                     border border-void-800/60 hover:border-void-600/70 text-void-300
                     hover:text-void-100 rounded transition-all duration-200
                     disabled:opacity-40 disabled:cursor-not-allowed
                     hover:shadow-[0_0_20px_rgba(107,31,208,0.15)]"
            >
              {{ authLoading ? '···' : activeTab }}
            </button>
          </form>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{
  close: []
  authenticated: []
}>()

const { login, register, authError, fieldErrors, authLoading } = useAuth()

const activeTab = ref<'login' | 'register'>('login')
const username = ref('')
const password = ref('')

function switchTab(tab: 'login' | 'register') {
  activeTab.value = tab
  authError.value = ''
  fieldErrors.value = {}
}

// Reset state when modal is closed/reopened
watch(() => props.open, (open) => {
  if (!open) {
    authError.value = ''
    fieldErrors.value = {}
  }
})

async function handleSubmit() {
  try {
    if (activeTab.value === 'login') {
      await login(username.value, password.value)
      username.value = ''
      password.value = ''
      emit('authenticated')
      emit('close')
    } else {
      await register(username.value, password.value)
      username.value = ''
      password.value = ''
      emit('authenticated')
      emit('close')
    }
  } catch {
    // errors already set in composable
  }
}
</script>
