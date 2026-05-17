import { useState, type FormEvent } from 'react'
import { Navigate, Link } from 'react-router-dom'
import { useRegister } from '@/features/auth/useRegister'
import { Button } from '@/shared/ui/button'

export function RegisterPage() {
  const { submit, error, pending } = useRegister()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [fieldError, setFieldError] = useState<string | null>(null)
  const [done, setDone] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setFieldError(null)
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
      setFieldError('Имя пользователя: только латиница, цифры и _')
      return
    }
    const ok = await submit({ username, email, full_name: fullName, password })
    if (ok) setDone(true)
  }

  if (done) return <Navigate to="/articles" replace />

  return (
    <div className="min-h-svh flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <h1 className="text-2xl font-bold tracking-tight text-center mb-6">Регистрация</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">Имя пользователя</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Латиница, цифры и _"
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Email</label>
            <input
              type="email"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium mb-1 block">Полное имя</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
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
          {(fieldError || error) && (
            <p className="text-sm text-destructive">{fieldError ?? error}</p>
          )}
          <Button type="submit" className="w-full" disabled={pending}>
            {pending ? 'Регистрация...' : 'Зарегистрироваться'}
          </Button>
        </form>
        <p className="text-sm text-muted-foreground text-center mt-4">
          Уже есть аккаунт?{' '}
          <Link to="/login" className="text-primary underline-offset-4 hover:underline">
            Войти
          </Link>
        </p>
      </div>
    </div>
  )
}
