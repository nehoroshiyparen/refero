import {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  type ReactNode,
} from 'react'
import { getMe } from '@/entities/auth/api'
import { setAccessToken, loadAccessToken } from '@/shared/api/client'
import type { UserProfile, RoleName } from '@/entities/auth/types'

type AuthState = {
  user: UserProfile | null
  loading: boolean
  hasRole: (...roles: RoleName[]) => boolean
  loginWithToken: (token: string) => Promise<boolean>
  clearUser: () => void
  tryLoadUser: () => Promise<void>
}

const AuthContext = createContext<AuthState | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = loadAccessToken()
    if (!token) {
      setLoading(false)
      return
    }

    getMe()
      .then((u) => setUserState(u))
      .catch(() => setAccessToken(null))
      .finally(() => setLoading(false))
  }, [])

  const loginWithToken = useCallback(async (token: string) => {
    setAccessToken(token)
    const u = await getMe()
    setUserState(u)
    return true
  }, [])

  const clearUser = useCallback(() => {
    setAccessToken(null)
    setUserState(null)
  }, [])

  const tryLoadUser = useCallback(async () => {
    const u = await getMe()
    setUserState(u)
  }, [])

  const hasRole = useCallback(
    (...roles: RoleName[]) => {
      if (!user) return false
      return user.roles.some((r) => roles.includes(r))
    },
    [user],
  )

  return (
    <AuthContext.Provider value={{ user, loading, hasRole, loginWithToken, clearUser, tryLoadUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
