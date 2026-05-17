import { useState } from 'react'
import { logout } from '@/entities/auth/api'
import { useAuth } from '@/app/providers/AuthProvider'

export function useLogout() {
  const { clearUser } = useAuth()
  const [pending, setPending] = useState(false)

  const submit = async () => {
    setPending(true)
    try {
      await logout()
    } catch {
      // ignore logout errors
    } finally {
      clearUser()
      setPending(false)
    }
  }

  return { submit, pending }
}
