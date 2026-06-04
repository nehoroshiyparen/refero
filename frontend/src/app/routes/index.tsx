import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from '@/app/providers/AuthProvider'
import { LandingPage } from '../../pages/landing'
import { LoginPage } from '../../pages/login'
import { RegisterPage } from '../../pages/register'
import { ArticlesPage, ArticleDetailPage, CreateArticlePage, EditArticlePage, MyArticlesPage, ReviewPage } from '../../pages/articles'
import { AssignmentsPage, AssignmentReviewPage } from '../../pages/reviews'
import { ProfilePage, PublicProfilePage } from '../../pages/profile'
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
  if (user && !user.roles.some((r) => roles.includes(r))) {
    return <Navigate to="/articles" replace />
  }
  return <>{children}</>
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<RequireGuest><LandingPage /></RequireGuest>} />
        <Route path="/login" element={<RequireGuest><LoginPage /></RequireGuest>} />
        <Route path="/register" element={<RequireGuest><RegisterPage /></RequireGuest>} />
        <Route path="/articles" element={<RequireAuth><ArticlesPage /></RequireAuth>} />
        <Route path="/articles/new" element={<RequireAuth><CheckRole roles={['AUTHOR', 'ADMIN']}><CreateArticlePage /></CheckRole></RequireAuth>} />
        <Route path="/articles/:id" element={<RequireAuth><ArticleDetailPage /></RequireAuth>} />
        <Route path="/articles/:id/review" element={<RequireAuth><ReviewPage /></RequireAuth>} />
        <Route path="/articles/:id/edit" element={<RequireAuth><CheckRole roles={['AUTHOR', 'ADMIN']}><EditArticlePage /></CheckRole></RequireAuth>} />
        <Route path="/my-articles" element={<RequireAuth><MyArticlesPage /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/users/:id" element={<PublicProfilePage />} />
        <Route path="/reviews/assignments" element={<RequireAuth><CheckRole roles={['REVIEWER']}><AssignmentsPage /></CheckRole></RequireAuth>} />
        <Route path="/reviews/assignments/:assignmentId" element={<RequireAuth><CheckRole roles={['REVIEWER']}><AssignmentReviewPage /></CheckRole></RequireAuth>} />
      </Routes>
    </BrowserRouter>
  )
}
