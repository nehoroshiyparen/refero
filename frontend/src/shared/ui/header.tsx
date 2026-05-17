import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { logout } from '@/entities/auth/api'
import { Button } from './button'

export function Header() {
  const { user, loading, clearUser } = useAuth()
  const navigate = useNavigate()

  if (loading) {
    return (
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <span className="text-xl font-bold tracking-tight">Refero</span>
          <div className="w-32" />
        </div>
      </header>
    )
  }

  if (!user) {
    return (
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <a href="/" className="text-xl font-bold tracking-tight">Refero</a>
          <nav className="hidden sm:flex items-center gap-6">
            <a href="/#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Возможности</a>
            <a href="/#workflow" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Процесс</a>
            <a href="/#tech-stack" className="text-sm text-muted-foreground hover:text-foreground transition-colors">API</a>
          </nav>
          <div className="flex items-center gap-2">
            <a href="/login"><Button variant="ghost" size="sm">Войти</Button></a>
            <a href="/register"><Button size="sm">Начать</Button></a>
          </div>
        </div>
      </header>
    )
  }

  const handleLogout = async () => {
    try { await logout() } catch {}
    clearUser()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <a href="/articles" className="text-xl font-bold tracking-tight">Refero</a>
        <nav className="flex items-center gap-6">
          <a href="/articles" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Статьи</a>
          {user.author_profile && (
            <a href="/my-articles" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Авторство</a>
          )}
          {user.reviewer_profile && (
            <a href="/reviews/assignments" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Рецензирование</a>
          )}
        </nav>
        <div className="flex items-center gap-3">
          <a href="/profile" className="text-sm text-muted-foreground hover:text-foreground transition-colors">{user.full_name}</a>
          <Button variant="outline" size="sm" onClick={handleLogout}>Выйти</Button>
        </div>
      </div>
    </header>
  )
}
