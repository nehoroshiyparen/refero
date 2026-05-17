import { useAuth } from '@/app/providers/AuthProvider'
import type { RoleName } from '@/entities/auth/types'

export function useRequireRole(...roles: RoleName[]) {
  const { user, hasRole } = useAuth()

  if (!user) return { allowed: false, reason: 'unauthenticated' as const }
  if (!hasRole(...roles)) return { allowed: false, reason: 'forbidden' as const }

  return { allowed: true as const, reason: null }
}
