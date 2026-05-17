import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { LandingPage } from '../../pages/landing'
import { LoginPage } from '../../pages/login'
import { RegisterPage } from '../../pages/register'
import { ArticlesPage, ArticleDetailPage, CreateArticlePage, EditArticlePage, MyArticlesPage } from '../../pages/articles'
import { ProfilePage } from '../../pages/profile'
import type { RoleName } from '@/entities/auth/types'

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return <>{children}</>
}

function RequireGuest({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  if (loading) return null
  if (user) return <Navigate to="/articles" replace />
  return <>{children}</>
}

function CheckRole({ children, roles }: { children: React.ReactNode; roles: RoleName[] }) {
  const { user } = useAuth()
  if (user && !roles.includes(user.role_name)) {
    return <Navigate to="/articles" replace />
  }
  return <>{children}</>
}

function Placeholder({ title }: { title: string }) {
  return (
    <div className="min-h-svh flex items-center justify-center text-muted-foreground text-lg">
      {title} — coming soon
    </div>
  )
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RequireGuest><LandingPage /></RequireGuest>} />
        <Route path="/login" element={<RequireGuest><LoginPage /></RequireGuest>} />
        <Route path="/register" element={<RequireGuest><RegisterPage /></RequireGuest>} />
        <Route path="/articles" element={<ArticlesPage />} />
        <Route path="/articles/new" element={<RequireAuth><CheckRole roles={['AUTHOR', 'ADMIN']}><CreateArticlePage /></CheckRole></RequireAuth>} />
        <Route path="/articles/:id" element={<ArticleDetailPage />} />
        <Route path="/articles/:id/edit" element={<RequireAuth><CheckRole roles={['AUTHOR', 'ADMIN']}><EditArticlePage /></CheckRole></RequireAuth>} />
        <Route path="/my-articles" element={<RequireAuth><MyArticlesPage /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/reviews/assignments" element={<RequireAuth><CheckRole roles={['REVIEWER']}><Placeholder title="Review Assignments" /></CheckRole></RequireAuth>} />
      </Routes>
    </BrowserRouter>
  )
}
