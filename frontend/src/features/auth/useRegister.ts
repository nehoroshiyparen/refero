import { useState } from 'react'
import { register } from '@/entities/auth/api'
import { useAuth } from '@/app/providers/AuthProvider'
import type { RegisterRequest } from '@/entities/auth/types'

export function useRegister() {
  const { loginWithToken } = useAuth()
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)

  const submit = async (data: RegisterRequest) => {
    setPending(true)
    setError(null)
    try {
      const auth = await register(data)
      const ok = await loginWithToken(auth.access_token)
      if (!ok) throw new Error('Ошибка загрузки профиля')
      return true
    } catch (e: any) {
      setError(e.message ?? 'Ошибка регистрации')
      return false
    } finally {
      setPending(false)
    }
  }

  return { submit, error, pending }
}
