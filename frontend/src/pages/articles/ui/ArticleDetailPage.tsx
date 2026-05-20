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
  registerView,
  addAuthor,
  removeAuthor,
} from '@/entities/article/api'
import { getUsers } from '@/entities/user/api'
import type { ArticleFullPayload, ArticleVersionPayload } from '@/entities/article/types'
import type { UserBrief } from '@/entities/user/types'

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

  const [showAddAuthor, setShowAddAuthor] = useState(false)
  const [authorSearchQuery, setAuthorSearchQuery] = useState('')
  const [authorSearchResults, setAuthorSearchResults] = useState<UserBrief[]>([])
  const [authorSearchLoading, setAuthorSearchLoading] = useState(false)

  const isCreator = user && article && user.id === article.creator_id
  const isCoAuthor = user && article && article.authors.some((a) => a.author_id === user.id)

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
    if (!id || !article || !user) return
    const isAuthor = user.id === article.creator_id || article.authors.some((a) => a.author_id === user.id)
    if (isAuthor) return
    registerView(id).catch(() => {})
  }, [id, article, user])

  const shouldLoadVersions = user && article && (isCreator || isCoAuthor)

  useEffect(() => {
    if (!id || !shouldLoadVersions) return
    setVersionsLoading(true)
    getArticleVersions(id)
      .then(setVersions)
      .catch(() => {})
      .finally(() => setVersionsLoading(false))
  }, [id, shouldLoadVersions])

  useEffect(() => {
    if (!authorSearchQuery.trim() || authorSearchQuery.length < 2) {
      setAuthorSearchResults([])
      return
    }
    setAuthorSearchLoading(true)
    const timer = setTimeout(() => {
      getUsers({ query: authorSearchQuery, limit: 10 })
        .then(setAuthorSearchResults)
        .catch(() => setAuthorSearchResults([]))
        .finally(() => setAuthorSearchLoading(false))
    }, 300)
    return () => clearTimeout(timer)
  }, [authorSearchQuery])

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
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  const handleAddAuthor = async (authorId: string) => {
    if (!id) return
    try {
      await addAuthor(id, authorId)
      setShowAddAuthor(false)
      setAuthorSearchQuery('')
      setAuthorSearchResults([])
      loadArticle()
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  const handleRemoveAuthor = async (authorId: string) => {
    if (!id) return
    if (!confirm('Удалить соавтора?')) return
    try {
      await removeAuthor(id, authorId)
      loadArticle()
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
            {(isCreator || isCoAuthor) && article.status === 'DRAFT' && (
              <Button size="sm" variant="outline" onClick={() => navigate(`/articles/${id}/edit`)}>
                Редактировать
              </Button>
            )}
            {isCreator && article.status === 'DRAFT' && (
              <Button size="sm" onClick={handleSubmitForApproval}>
                На согласование
              </Button>
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

        {/* ── Authors management (creator only) ── */}
        {isCreator && (
          <section className="border-t pt-6">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold">Соавторы</h2>
              <Button size="sm" variant="outline" onClick={() => setShowAddAuthor(!showAddAuthor)}>
                {showAddAuthor ? 'Отмена' : 'Добавить соавтора'}
              </Button>
            </div>

            {showAddAuthor && (
              <div className="mb-4 space-y-2">
                <input
                  type="text"
                  placeholder="Поиск по имени или email..."
                  value={authorSearchQuery}
                  onChange={(e) => setAuthorSearchQuery(e.target.value)}
                  className="w-full rounded-lg border px-3 py-2 text-sm"
                  autoFocus
                />
                {authorSearchLoading && (
                  <p className="text-xs text-muted-foreground">Поиск...</p>
                )}
                {authorSearchResults.length > 0 && (
                  <div className="rounded-lg border divide-y max-h-48 overflow-y-auto">
                    {authorSearchResults
                      .filter((u) => !article.authors.some((a) => a.author_id === u.id))
                      .map((u) => (
                        <button
                          key={u.id}
                          type="button"
                          className="w-full text-left px-3 py-2 text-sm hover:bg-muted transition-colors flex items-center justify-between"
                          onClick={() => handleAddAuthor(u.id)}
                        >
                          <span>{u.full_name || u.username}</span>
                          <span className="text-xs text-muted-foreground">{u.email}</span>
                        </button>
                      ))}
                  </div>
                )}
                {authorSearchQuery.length >= 2 && authorSearchResults.length === 0 && !authorSearchLoading && (
                  <p className="text-xs text-muted-foreground">Ничего не найдено</p>
                )}
              </div>
            )}

            <div className="space-y-1">
              {article.authors.map((a) => {
                const isRemovable = a.author_id !== user?.id
                return (
                  <div key={a.author_id} className="flex items-center justify-between rounded-lg border px-3 py-2">
                    <div>
                      <span className="text-sm font-medium">{a.name}</span>
                      {a.author_id === article.creator_id && (
                        <span className="ml-2 text-xs text-muted-foreground">(создатель)</span>
                      )}
                      <p className="text-xs text-muted-foreground">{a.email}</p>
                    </div>
                    {isRemovable && (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-destructive"
                        onClick={() => handleRemoveAuthor(a.author_id)}
                      >
                        Удалить
                      </Button>
                    )}
                  </div>
                )
              })}
            </div>
          </section>
        )}

        <div className="border-t pt-6 space-y-6 mt-6">
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

        {shouldLoadVersions && (
          <section className="border-t pt-6 mt-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Версии</h2>
              {isCreator && (
                <Button size="sm" onClick={handleCreateVersion}>
                  Создать версию
                </Button>
              )}
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
                      <div className="flex items-center gap-2 ml-4 shrink-0 flex-wrap">
                        {(isCreator || isCoAuthor) && v.status === 'DRAFT' && (
                          <Button size="sm" variant="outline" onClick={() => navigate(`/articles/${id}/edit?version=${v.id}`)}>
                            Редактировать
                          </Button>
                        )}
                        {isCreator && v.status === 'DRAFT' && (
                          <Button size="sm" variant="outline" onClick={handleSubmitForApproval}>
                            На согласование
                          </Button>
                        )}
                        {isCreator && !isCurrent && (
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
                        {isCoAuthor && v.status === 'PENDING_APPROVAL' && (
                          <Button size="sm" onClick={() => navigate(`/articles/${id}/review?version=${v.id}`)}>
                            Рассмотреть
                          </Button>
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
