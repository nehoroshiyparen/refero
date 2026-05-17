import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import {
  getArticle,
  getArticleVersions,
  createArticleVersion,
  setCurrentVersion,
  deleteArticleVersion,
  submitForApproval,
} from '@/entities/article/api'
import type { ArticleFullPayload, ArticleVersionPayload } from '@/entities/article/types'

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

export function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()
  const [article, setArticle] = useState<ArticleFullPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [versions, setVersions] = useState<ArticleVersionPayload[]>([])
  const [versionsLoading, setVersionsLoading] = useState(false)

  const isCreator = user && article && user.id === article.creator_id

  const loadArticle = () => {
    if (!id) return
    setLoading(true)
    getArticle(id)
      .then(setArticle)
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadArticle()
  }, [id])

  useEffect(() => {
    if (!id || !isCreator) return
    setVersionsLoading(true)
    getArticleVersions(id)
      .then(setVersions)
      .catch(() => {})
      .finally(() => setVersionsLoading(false))
  }, [id, isCreator])

  const handleCreateVersion = async () => {
    if (!id) return
    try {
      const v = await createArticleVersion(id)
      if (article) setArticle({ ...article, ...v as any })
      const updated = await getArticleVersions(id)
      setVersions(updated)
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  const handleSetCurrent = async (versionId: string) => {
    if (!id) return
    try {
      const updated = await setCurrentVersion(id, versionId)
      setArticle(updated)
      const updatedVersions = await getArticleVersions(id)
      setVersions(updatedVersions)
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  const handleDeleteVersion = async (versionId: string) => {
    if (!id) return
    if (!confirm('Удалить версию?')) return
    try {
      await deleteArticleVersion(id, versionId)
      setVersions(versions.filter((v) => v.id !== versionId))
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  const handleSubmitForApproval = async () => {
    if (!id) return
    try {
      await submitForApproval(id)
      loadArticle()
      const updatedVersions = await getArticleVersions(id)
      setVersions(updatedVersions)
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  if (loading) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center text-muted-foreground">Загрузка...</div>
      </div>
    )
  }

  if (error || !article) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <p className="text-muted-foreground">{error ?? 'Статья не найдена'}</p>
          <Button variant="outline" onClick={() => navigate('/articles')}>Назад к списку</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 flex-1 max-w-4xl">
        <div className="flex items-center justify-between mb-6">
          <Link to="/articles" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            &larr; Назад к статьям
          </Link>
          <div className="flex items-center gap-2">
            {isCreator && article.status === 'DRAFT' && (
              <>
                <Button size="sm" variant="outline" onClick={() => navigate(`/articles/${id}/edit`)}>
                  Редактировать
                </Button>
                <Button size="sm" variant="outline" onClick={handleSubmitForApproval}>
                  Отправить на согласование
                </Button>
              </>
            )}
            <span className={`rounded-full px-3 py-1 text-xs font-medium ${statusColors[article.status] || ''}`}>
              {statusLabels[article.status] || article.status}
            </span>
          </div>
        </div>

        <h1 className="text-3xl font-bold tracking-tight mb-3">{article.title}</h1>

        {article.authors.length > 0 && (
          <p className="text-sm text-muted-foreground mb-2">
            Авторы: {article.authors.map((a) => a.name).join(', ')}
          </p>
        )}

        <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground mb-6">
          {article.journal && <span>{article.journal.name}</span>}
          <span>{article.language.toUpperCase()}</span>
          {article.published_at && (
            <span>Опубликована {new Date(article.published_at).toLocaleDateString('ru-RU')}</span>
          )}
        </div>

        <div className="border-t pt-6 space-y-6">
          {article.abstract && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Аннотация</h2>
              <p className="text-sm text-muted-foreground leading-relaxed">{article.abstract}</p>
            </section>
          )}

          {article.keywords.length > 0 && (
            <section>
              <h2 className="text-lg font-semibold mb-2">Ключевые слова</h2>
              <div className="flex flex-wrap gap-2">
                {article.keywords.map((kw) => (
                  <span
                    key={kw}
                    className="rounded-full border px-3 py-1 text-xs text-muted-foreground"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </section>
          )}

          <section className="border-t pt-6">
            <h2 className="text-lg font-semibold mb-3">Информация</h2>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Просмотров</span>
                <p className="font-medium">{article.view_count}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Скачиваний</span>
                <p className="font-medium">{article.download_count}</p>
              </div>
              <div>
                <span className="text-muted-foreground">Версия</span>
                <p className="font-medium">{article.version_number}</p>
              </div>
              {article.created_at && (
                <div>
                  <span className="text-muted-foreground">Создана</span>
                  <p className="font-medium">{new Date(article.created_at).toLocaleDateString('ru-RU')}</p>
                </div>
              )}
              {article.updated_at && (
                <div>
                  <span className="text-muted-foreground">Обновлена</span>
                  <p className="font-medium">{new Date(article.updated_at).toLocaleDateString('ru-RU')}</p>
                </div>
              )}
            </div>
          </section>

          {article.citations.length > 0 && (
            <section className="border-t pt-6">
              <h2 className="text-lg font-semibold mb-3">Цитирования ({article.citations.length})</h2>
              <ul className="space-y-2 text-sm text-muted-foreground">
                {article.citations.map((c) => (
                  <li key={c.id} className="border-l-2 pl-3">
                    {c.raw_reference || c.doi || 'Без названия'}
                  </li>
                ))}
              </ul>
            </section>
          )}
        </div>

        {isCreator && (
          <section className="border-t pt-6 mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Версии</h2>
              <Button size="sm" onClick={handleCreateVersion}>
                Создать версию
              </Button>
            </div>

            {versionsLoading ? (
              <p className="text-sm text-muted-foreground">Загрузка...</p>
            ) : versions.length === 0 ? (
              <p className="text-sm text-muted-foreground">Нет версий</p>
            ) : (
              <div className="space-y-2">
                {versions.map((v) => {
                  const isCurrent = v.id === article.current_version_id
                  return (
                    <div
                      key={v.id}
                      className={`rounded-xl border p-4 flex items-center justify-between ${isCurrent ? 'border-primary/50 bg-primary/5' : ''}`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="font-medium text-sm">Версия {v.version_number}</span>
                          {isCurrent && (
                            <span className="rounded-full bg-primary/10 text-primary text-xs px-2 py-0.5 font-medium">
                              Текущая
                            </span>
                          )}
                          {v.status !== article.status && (
                            <span className={`rounded-full px-2 py-0.5 text-xs ${statusColors[v.status] || ''}`}>
                              {statusLabels[v.status] || v.status}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground truncate mt-0.5">{v.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(v.created_at).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 ml-4 shrink-0">
                        {!isCurrent && (
                          <>
                            <Button size="sm" variant="outline" onClick={() => handleSetCurrent(v.id)}>
                              Сделать текущей
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="text-destructive"
                              onClick={() => handleDeleteVersion(v.id)}
                            >
                              Удалить
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  )
}
