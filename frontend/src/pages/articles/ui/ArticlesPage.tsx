import { useState, useEffect, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import { getArticles } from '@/entities/article/api'
import { getJournals } from '@/entities/journal/api'
import type { ArticlePayload } from '@/entities/article/types'
import type { JournalPayload } from '@/entities/journal/types'

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

export function ArticlesPage() {
  const { user, hasRole } = useAuth()
  const navigate = useNavigate()
  const [articles, setArticles] = useState<ArticlePayload[]>([])
  const [journals, setJournals] = useState<JournalPayload[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [journalId, setJournalId] = useState('')

  const journalMap = new Map(journals.map((j) => [j.id, j.name]))

  useEffect(() => {
    getJournals().then(setJournals)
  }, [])

  useEffect(() => {
    setLoading(true)
    getArticles({ query: query || undefined, journal_id: journalId || undefined, status: 'PUBLISHED' })
      .then(setArticles)
      .finally(() => setLoading(false))
  }, [query, journalId])

  const handleSearch = (e: FormEvent) => {
    e.preventDefault()
    const form = e.target as HTMLFormElement
    const fd = new FormData(form)
    setQuery((fd.get('query') as string) || '')
  }

  const canCreate = hasRole('AUTHOR', 'ADMIN')

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 flex-1">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold tracking-tight">Статьи</h1>
          {canCreate && (
            <Button onClick={() => navigate('/articles/new')}>Создать статью</Button>
          )}
        </div>

        <div className="flex flex-wrap gap-3 mb-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              name="query"
              defaultValue={query}
              placeholder="Поиск по названию..."
              className="w-64 rounded-md border border-input bg-background px-3 py-2 text-sm"
            />
            <Button type="submit" variant="outline" size="sm">Поиск</Button>
          </form>

          <select
            value={journalId}
            onChange={(e) => setJournalId(e.target.value)}
            className="rounded-md border border-input bg-background px-3 py-2 text-sm"
          >
            <option value="">Все журналы</option>
            {journals.map((j) => (
              <option key={j.id} value={j.id}>{j.name}</option>
            ))}
          </select>
        </div>

        {loading ? (
          <div className="text-center text-muted-foreground py-12">Загрузка...</div>
        ) : articles.length === 0 ? (
          <div className="text-center text-muted-foreground py-12">
            {query || journalId ? 'Ничего не найдено' : 'Статей пока нет'}
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
                      {a.journal_id && journalMap.has(a.journal_id) && (
                        <span>{journalMap.get(a.journal_id)}</span>
                      )}
                      <span>{a.language.toUpperCase()}</span>
                      {a.created_at && (
                        <span>{new Date(a.created_at).toLocaleDateString('ru-RU')}</span>
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
