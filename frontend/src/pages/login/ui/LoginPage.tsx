import { useState, type FormEvent } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { useLogin } from '@/features/auth/useLogin'
import { Button } from '@/shared/ui/button'

export function LoginPage() {
  const { submit, error, pending } = useLogin()
  const [login, setLogin] = useState('')
  const [password, setPassword] = useState('')
  const [done, setDone] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const isEmail = login.includes('@')
    const ok = await submit(
      isEmail ? { email: login, password } : { username: login, password },
    )
    if (ok) setDone(true)
  }

  if (done) return <Navigate to="/articles" replace />

  return (
    <div className="min-h-svh flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold tracking-tight text-center mb-6">Войти</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">Логин или email</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Пароль</label>
            <input
              type="password"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? 'Вход...' : 'Войти'}
          </Button>
        </form>
        <p className="text-sm text-muted-foreground text-center mt-4">
          Нет аккаунта?{' '}
          <Link to="/register" className="text-primary underline-offset-4 hover:underline">
            Зарегистрироваться
          </Link>
        </p>
      </div>
    </div>
  )
}
