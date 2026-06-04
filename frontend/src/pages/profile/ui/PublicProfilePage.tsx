import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { getUser } from '@/entities/user/api'
import { getArticles } from '@/entities/article/api'
import type { UserProfile } from '@/entities/user/types'
import type { ArticlePayload } from '@/entities/article/types'

const statusLabels: Record<string, string> = {
  PUBLISHED: 'Опубликована',
}

const statusColors: Record<string, string> = {
  PUBLISHED: 'text-green-600',
}

export function PublicProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [articles, setArticles] = useState<ArticlePayload[]>([])

  useEffect(() => {
    if (!id) return
    setLoading(true)
    Promise.all([
      getUser(id),
      getArticles({ author_id: id, status: 'PUBLISHED', is_visible: true }),
    ])
      .then(([u, a]) => {
        setProfile(u)
        setArticles(a)
      })
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center text-muted-foreground">Загрузка...</div>
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <p className="text-destructive">{error ?? 'Пользователь не найден'}</p>
          <Button variant="outline" onClick={() => navigate('/articles')}>К списку статей</Button>
        </div>
      </div>
    )
  }

  const initials = profile.full_name
    .split(' ')
    .map((s) => s[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 flex-1">
        <Link to="/articles" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
          &larr; К списку статей
        </Link>

        <div className="flex flex-col md:flex-row gap-8 mt-4">
          {/* sidebar */}
          <aside className="md:w-72 shrink-0">
            <div className="flex md:flex-col items-center md:items-start gap-4 md:gap-3">
              <div className="w-16 h-16 md:w-[120px] md:h-[120px] rounded-full bg-muted flex items-center justify-center text-xl md:text-4xl font-bold text-muted-foreground shrink-0">
                {initials}
              </div>
              <div className="text-center md:text-left">
                <h1 className="text-xl md:text-2xl font-bold">{profile.full_name}</h1>
                <p className="text-sm text-muted-foreground">{profile.username}</p>
              </div>
            </div>

            {profile.author_profile?.bio && (
              <p className="text-sm mt-4 text-center md:text-left">{profile.author_profile.bio}</p>
            )}

            <div className="space-y-2 mt-4 text-sm text-muted-foreground">
              {profile.author_profile?.organization && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span>{profile.author_profile.organization}</span>
                </div>
              )}
              {profile.author_profile?.position && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span>{profile.author_profile.position}</span>
                </div>
              )}
              {profile.author_profile?.orcid && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span>{profile.author_profile.orcid}</span>
                </div>
              )}
            </div>

            <div className="flex gap-4 mt-6 text-sm justify-center md:justify-start">
              <span className="font-bold">{articles.length}</span>{' '}
              <span className="text-muted-foreground">статей</span>
            </div>
          </aside>

          {/* main content */}
          <main className="flex-1 min-w-0">
            <h2 className="text-lg font-semibold mb-4">Статьи</h2>
            {articles.length === 0 ? (
              <p className="text-sm text-muted-foreground py-8 text-center">Статей пока нет</p>
            ) : (
              <div className="space-y-2">
                {articles.map((a) => (
                  <div
                    key={a.id}
                    className="rounded-xl border p-5 hover:bg-muted/30 transition-colors cursor-pointer"
                    onClick={() => navigate(`/articles/${a.id}`)}
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="min-w-0 flex-1">
                        <h3 className="font-semibold text-base truncate">{a.title}</h3>
                        {a.abstract && (
                          <p className="text-sm text-muted-foreground mt-1 line-clamp-1">{a.abstract}</p>
                        )}
                        <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                          <span className={`font-medium ${statusColors[a.status] || ''}`}>
                            {statusLabels[a.status] || a.status}
                          </span>
                          {a.language && <span>{a.language.toUpperCase()}</span>}
                          <span>{a.view_count} просмотров</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
