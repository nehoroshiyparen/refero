import { useState } from 'react'
import { login } from '@/entities/auth/api'
import { useAuth } from '@/app/providers/AuthProvider'
import type { LoginRequest } from '@/entities/auth/types'

export function useLogin() {
  const { loginWithToken } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)

  const submit = async (data: LoginRequest) => {
    setPending(true)
    setError(null)
    try {
      const auth = await login(data)
      await loginWithToken(auth.access_token)
      return true
    } catch (e: any) {
      setError(e.message ?? 'Ошибка входа')
      return false
    } finally {
      setPending(false)
    }
  }

  return { submit, error, pending }
}
