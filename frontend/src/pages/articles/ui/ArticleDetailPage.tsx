import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { PdfViewer } from '@/shared/ui/pdf-viewer'
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
  hideArticle,
  showArticle,
  getDownloadUrl,
} from '@/entities/article/api'
import { getUsers } from '@/entities/user/api'
import { getVersionAssignment, getReviewByAssignment, getComments } from '@/entities/review/api'
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
  const [versionReviewInfo, setVersionReviewInfo] = useState<Record<string, {needsChanges: boolean; commentCount: number}>>({})

  const [showAddAuthor, setShowAddAuthor] = useState(false)
  const [authorSearchQuery, setAuthorSearchQuery] = useState('')
  const [authorSearchResults, setAuthorSearchResults] = useState<UserBrief[]>([])
  const [authorSearchLoading, setAuthorSearchLoading] = useState(false)

  const [reviewAssignment, setReviewAssignment] = useState<any | null>(null)
  const [reviewDecision, setReviewDecision] = useState<any | null>(null)
  const [reviewComments, setReviewComments] = useState<any[]>([])
  const [reviewLoading, setReviewLoading] = useState(false)

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
    ;(async () => {
      try {
        const v = await getArticleVersions(id)
        const info: Record<string, {needsChanges: boolean; commentCount: number}> = {}
        await Promise.all(v.map(async (ver) => {
          try {
            const assignment = await getVersionAssignment(id, ver.id)
            if (assignment?.review_status === 'REQUESTING_CHANGES') {
              const comments = await getComments(ver.id)
              info[ver.id] = { needsChanges: true, commentCount: comments.length }
            } else {
              info[ver.id] = { needsChanges: false, commentCount: 0 }
            }
          } catch {
            info[ver.id] = { needsChanges: false, commentCount: 0 }
          }
        }))
        setVersions(v)
        setVersionReviewInfo(info)
      } catch {
        // ignore
      } finally {
        setVersionsLoading(false)
      }
    })()
  }, [id, shouldLoadVersions])

  useEffect(() => {
    if (!id || !article || article.status !== 'REVIEW' || !article.current_version_id) return
    setReviewLoading(true)
    getVersionAssignment(id, article.current_version_id)
      .then((assignment) => {
        setReviewAssignment(assignment)
        if (assignment?.id) {
          getReviewByAssignment(assignment.id).then(setReviewDecision)
        }
      })
      .catch(() => {})
    getComments(article.current_version_id)
      .then(setReviewComments)
      .catch(() => {})
      .finally(() => setReviewLoading(false))
  }, [id, article?.status, article?.current_version_id])

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
    const v = versions.find((x) => x.id === versionId)
    if (v?.status === 'REJECTED') {
      alert('Нельзя сделать отклонённую версию текущей')
      return
    }
    try {
      const updated = await setCurrentVersion(id, versionId)
      setArticle(updated)
      const updatedVersions = await getArticleVersions(id)
      setVersions(updatedVersions)
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    }
  }

  const handleToggleVisibility = async () => {
    if (!id || !article) return
    try {
      const result = article.is_visible ? await hideArticle(id) : await showArticle(id)
      setArticle({ ...article, is_visible: result.is_visible })
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
      const updated = await getArticleVersions(id)
      const info: Record<string, {needsChanges: boolean; commentCount: number}> = {}
      await Promise.all(updated.map(async (ver) => {
        try {
          const assignment = await getVersionAssignment(id, ver.id)
          if (assignment?.review_status === 'REQUESTING_CHANGES') {
            const comments = await getComments(ver.id)
            info[ver.id] = { needsChanges: true, commentCount: comments.length }
          } else {
            info[ver.id] = { needsChanges: false, commentCount: 0 }
          }
        } catch {
          info[ver.id] = { needsChanges: false, commentCount: 0 }
        }
      }))
      setVersions(updated)
      setVersionReviewInfo(info)
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
            {isCreator && (
              <Button size="sm" variant="outline" onClick={handleToggleVisibility}>
                {article.is_visible ? 'Скрыть' : 'Показать'}
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
            Авторы:{' '}
            {article.authors.map((a, i) => (
              <span key={a.author_id}>
                {i > 0 && ', '}
                <Link to={`/users/${a.author_id}`} className="hover:underline font-medium">
                  {a.name}
                </Link>
              </span>
            ))}
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
              {article.authors
                .filter((a) => a.author_id !== user?.id)
                .map((a) => {
                  const isRemovable = a.author_id !== user?.id
                  return (
                    <div key={a.author_id} className="flex items-center justify-between rounded-lg border px-3 py-2">
                      <div>
                        <Link to={`/users/${a.author_id}`} className="text-sm font-medium hover:underline">{a.name}</Link>
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
              {article.pdf_url && (
                <div className="col-span-full mt-2">
                  <a
                    href={article.pdf_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-border bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2"
                  >
                    Скачать PDF
                  </a>
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

          {article.pdf_url && (
            <section className="border-t pt-6">
              <h2 className="text-lg font-semibold mb-3">Просмотр PDF</h2>
              <PdfViewer pdfUrl={article.pdf_url} />
            </section>
          )}
        </div>

        {/* ── Review info for authors (REVIEW status) ── */}
        {article.status === 'REVIEW' && (isCreator || isCoAuthor) && (
          <section className="border-t pt-6 mt-6">
            <h2 className="text-lg font-semibold mb-3">Рецензирование</h2>
            {reviewLoading ? (
              <p className="text-sm text-muted-foreground">Загрузка...</p>
            ) : reviewAssignment ? (
              <div className="space-y-3">
                {reviewDecision ? (
                  <div className="rounded-lg border px-4 py-3">
                    <p className="text-sm font-medium">Решение рецензента</p>
                    <p className="text-sm mt-1">{reviewDecision.status === 'APPROVED' ? 'Одобрена' : reviewDecision.status === 'REJECTED' ? 'Отклонена' : 'Запрошены изменения'}</p>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">Статья передана на рецензирование. Ожидайте решения.</p>
                )}

                {reviewComments.length > 0 && (
                  <div className="space-y-2">
                    <p className="text-sm font-medium">Комментарии рецензента</p>
                    {reviewComments.map((c: any) => (
                      <div key={c.id} className="rounded-lg border px-3 py-2">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-xs font-medium">{c.user_name || 'Рецензент'}</span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(c.created_at).toLocaleString('ru-RU')}
                          </span>
                        </div>
                        <p className="text-sm">{c.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">Информация о рецензировании недоступна</p>
            )}
          </section>
        )}

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
                      className={`rounded-xl border p-4 ${isCurrent ? 'border-primary/50 bg-primary/5' : ''}`}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium text-sm">Версия {v.version_number}</span>
                          {isCurrent && (
                            <span className="rounded-full bg-primary/10 text-primary text-xs px-2 py-0.5 font-medium">
                              Текущая
                            </span>
                          )}
                          <span className={`rounded-full px-2 py-0.5 text-xs ${statusColors[v.status] || ''}`}>
                            {statusLabels[v.status] || v.status}
                          </span>
                          {versionReviewInfo[v.id]?.needsChanges && (
                            <span className="rounded-full bg-amber-100 text-amber-800 text-xs px-2 py-0.5 font-medium">
                              Требует изменений{versionReviewInfo[v.id].commentCount > 0 ? ` (${versionReviewInfo[v.id].commentCount})` : ''}
                            </span>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground truncate mt-0.5">{v.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(v.created_at).toLocaleDateString('ru-RU')}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 flex-wrap mt-3 pt-3 border-t">
                        {(isCreator || isCoAuthor) && (
                          <Button size="sm" variant="ghost" onClick={() => navigate(`/articles/${id}/review?version=${v.id}`)}>
                            Просмотр
                          </Button>
                        )}
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
                        {(v.pdf_url || v.pdf_path) && (
                          <a
                            href={v.pdf_url || getDownloadUrl(id!, v.id)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-xs font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 h-8 rounded-md px-3 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground"
                          >
                            Скачать PDF
                          </a>
                        )}
                        {isCreator && !isCurrent && v.status !== 'REJECTED' && (
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
