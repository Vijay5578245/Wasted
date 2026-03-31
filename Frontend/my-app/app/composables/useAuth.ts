interface User {
  id: number
  username: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

export interface FieldErrors {
  username?: string
  password?: string
}

export const useAuth = () => {
  const config = useRuntimeConfig()
  const API = config.public.apiBase as string

  const token = useCookie<string>('wasted_token', {
    default: () => '',
    maxAge: 60 * 60 * 24 * 30,
    sameSite: 'lax',
  })

  const user = useState<User | null>('auth_user', () => null)
  const authError = useState<string>('auth_error', () => '')
  const fieldErrors = useState<FieldErrors>('field_errors', () => ({}))
  const authLoading = useState<boolean>('auth_loading', () => false)

  const isLoggedIn = computed(() => !!token.value && !!user.value)

  async function fetchUser() {
    if (!token.value) return
    try {
      const data = await $fetch<User>(`${API}/me`, {
        headers: { Authorization: `Bearer ${token.value}` },
      })
      user.value = data
    } catch {
      token.value = ''
      user.value = null
    }
  }

  function parseErrors(e: any, fallback: string): string {
    fieldErrors.value = {}
    const detail = e?.data?.detail
    if (!detail) return e?.message ?? fallback

    if (Array.isArray(detail)) {
      const general: string[] = []
      for (const d of detail) {
        const field = d.loc?.[1] as keyof FieldErrors | undefined
        const msg: string = (d.msg ?? '').replace(/^Value error, /, '')
        if (field && field in { username: 1, password: 1 }) {
          fieldErrors.value[field] = msg
        } else {
          general.push(msg)
        }
      }
      return general.join(', ')
    }

    return String(detail)
  }

  async function login(username: string, password: string) {
    authError.value = ''
    fieldErrors.value = {}
    authLoading.value = true
    try {
      const data = await $fetch<TokenResponse>(`${API}/auth/login`, {
        method: 'POST',
        body: { username, password },
      })
      token.value = data.access_token
      await fetchUser()
    } catch (e: any) {
      authError.value = parseErrors(e, 'Login failed')
      throw e
    } finally {
      authLoading.value = false
    }
  }

  async function register(username: string, password: string) {
    authError.value = ''
    fieldErrors.value = {}
    authLoading.value = true
    try {
      const data = await $fetch<TokenResponse>(`${API}/auth/register`, {
        method: 'POST',
        body: { username, password },
      })
      token.value = data.access_token
      await fetchUser()
    } catch (e: any) {
      authError.value = parseErrors(e, 'Registration failed')
      throw e
    } finally {
      authLoading.value = false
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    authError.value = ''
    fieldErrors.value = {}
  }

  return {
    token, user, isLoggedIn,
    authError, fieldErrors, authLoading,
    login, register, logout, fetchUser,
  }
}
