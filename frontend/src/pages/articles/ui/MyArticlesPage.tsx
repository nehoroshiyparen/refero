import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import { getArticles } from '@/entities/article/api'
import type { ArticlePayload, ArticleStatus } from '@/entities/article/types'

const statusLabels: Record<string, string> = {
  DRAFT: 'Черновик',
  PENDING_APPROVAL: 'На согласовании',
  REVIEW: 'На рецензии',
  PUBLISHED: 'Опубликована',
  REJECTED: 'Отклонена',
}

const statusColors: Record<string, string> = {
  DRAFT: 'bg-muted text-muted-foreground',
  PENDING_APPROVAL: 'bg-blue-100 text-blue-700',
  REVIEW: 'bg-purple-100 text-purple-700',
  PUBLISHED: 'bg-green-100 text-green-700',
  REJECTED: 'bg-red-100 text-red-700',
}

const statusOptions: { value: string; label: string }[] = [
  { value: '', label: 'Все статусы' },
  { value: 'DRAFT', label: 'Черновик' },
  { value: 'PENDING_APPROVAL', label: 'На согласовании' },
  { value: 'REVIEW', label: 'На рецензии' },
  { value: 'PUBLISHED', label: 'Опубликована' },
  { value: 'REJECTED', label: 'Отклонена' },
]

export function MyArticlesPage() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [articles, setArticles] = useState<ArticlePayload[]>([])
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300)
    return () => clearTimeout(t)
  }, [search])

  useEffect(() => {
    if (!user) return
    setLoading(true)
    const filters: any = { author_id: user.id }
    if (debouncedSearch) filters.query = debouncedSearch
    if (statusFilter) filters.status = statusFilter as ArticleStatus
    getArticles(filters)
      .then(setArticles)
      .finally(() => setLoading(false))
  }, [user, debouncedSearch, statusFilter])

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 flex-1">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold tracking-tight">Мои статьи</h1>
          <Button onClick={() => navigate('/articles/new')}>Создать статью</Button>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <input
            className="w-full max-w-sm rounded-md border border-input bg-background px-3 py-2 text-sm"
            placeholder="Поиск по названию..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <select
            className="rounded-md border border-input bg-background px-3 py-2 text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            {statusOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="text-center text-muted-foreground py-12">Загрузка...</div>
        ) : articles.length === 0 ? (
          <div className="text-center text-muted-foreground py-12">
            <p className="mb-4">У вас пока нет статей</p>
            <Button onClick={() => navigate('/articles/new')}>Создать первую статью</Button>
          </div>
        ) : (
          <div className="space-y-3">
            {articles.map((a) => (
              <div
                key={a.id}
                className="rounded-xl border p-5 hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => navigate(`/articles/${a.id}`)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <h2 className="font-semibold text-lg truncate">{a.title}</h2>
                    <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                      {a.abstract || 'Нет аннотации'}
                    </p>
                    <div className="flex items-center gap-3 mt-3 text-xs text-muted-foreground">
                      <span>{a.language.toUpperCase()}</span>
                      <span>{a.view_count} просмотров</span>
                      {a.updated_at && (
                        <span>Обновлено {new Date(a.updated_at).toLocaleDateString('ru-RU')}</span>
                      )}
                    </div>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${statusColors[a.status] || ''}`}
                  >
                    {statusLabels[a.status] || a.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
