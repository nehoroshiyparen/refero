import { useState, useEffect } from 'react'
import { useParams, useNavigate, useSearchParams, Link } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import {
  getArticle,
  getArticleVersions,
  getArticleVersionById,
  getVersionApprovals,
  approveVersion,
} from '@/entities/article/api'
import { getVersionAssignment, getReviewByAssignment, getComments } from '@/entities/review'
import type { ArticleFullPayload, ArticleVersionPayload, ApprovalBrief } from '@/entities/article/types'
import type { CommentPayload, ReviewPayload } from '@/entities/review/types'

const statusLabels: Record<string, string> = {
  PENDING: 'Ожидает',
  APPROVED: 'Одобрено',
  REJECTED: 'Отклонено',
}

const statusColors: Record<string, string> = {
  PENDING: 'text-muted-foreground',
  APPROVED: 'text-green-600',
  REJECTED: 'text-red-600',
}

const reviewStatusLabels: Record<string, string> = {
  APPROVED: 'Одобрена',
  REJECTED: 'Отклонена',
  REQUESTING_CHANGES: 'Запрошены изменения',
}

const reviewStatusColors: Record<string, string> = {
  APPROVED: 'text-green-600',
  REJECTED: 'text-red-600',
  REQUESTING_CHANGES: 'text-amber-600',
}

export function ReviewPage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams, setSearchParams] = useSearchParams()
  const navigate = useNavigate()
  const { user } = useAuth()

  const versionIdFromUrl = searchParams.get('version')

  const [article, setArticle] = useState<ArticleFullPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [versionsList, setVersionsList] = useState<ArticleVersionPayload[]>([])
  const [versionId, setVersionId] = useState<string | null>(null)
  const [version, setVersion] = useState<ArticleVersionPayload | null>(null)
  const [versionLoading, setVersionLoading] = useState(false)

  const [approvals, setApprovals] = useState<ApprovalBrief[]>([])
  const [approvalsLoading, setApprovalsLoading] = useState(false)

  const [assignment, setAssignment] = useState<any | null>(null)
  const [review, setReview] = useState<ReviewPayload | null>(null)
  const [reviewLoading, setReviewLoading] = useState(false)

  const [comments, setComments] = useState<CommentPayload[]>([])
  const [commentsLoading, setCommentsLoading] = useState(false)

  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  const isCoAuthor = user && article?.authors.some((a) => a.author_id === user.id)
  const isCreator = user && article?.creator_id === user.id
  const canApprove = isCoAuthor || isCreator
  const myApproval = approvals.find((a) => a.approver_id === user?.id)

  useEffect(() => {
    if (!id || !user) return
    setLoading(true)
    getArticle(id)
      .then((a) => {
        setArticle(a)

        getArticleVersions(id)
          .then((versions) => {
            setVersionsList(versions)

            let targetVersionId: string | null = versionIdFromUrl

            if (!targetVersionId) {
              const pending = versions.find((v) => v.status === 'PENDING_APPROVAL')
              targetVersionId = pending?.id ?? a.current_version_id ?? null
            }

            if (!targetVersionId) {
              setError('Не указана версия')
              return
            }

            setVersionId(targetVersionId)
            loadVersionData(id, targetVersionId)
          })
          .catch(() => setError('Не удалось загрузить версии'))
      })
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [id, versionIdFromUrl, user])

  function loadVersionData(articleId: string, vId: string) {
    setVersionLoading(true)
    getArticleVersionById(articleId, vId)
      .then(setVersion)
      .catch(() => setError('Не удалось загрузить версию'))
      .finally(() => setVersionLoading(false))

    setApprovalsLoading(true)
    getVersionApprovals(articleId, vId)
      .then(setApprovals)
      .catch(() => {})
      .finally(() => setApprovalsLoading(false))

    setReviewLoading(true)
    getVersionAssignment(articleId, vId)
      .then((a) => {
        setAssignment(a)
        if (a?.id) {
          getReviewByAssignment(a.id).then((r) => setReview(r)).catch(() => {})
        } else {
          setReview(null)
        }
      })
      .catch(() => {})
      .finally(() => setReviewLoading(false))

    setCommentsLoading(true)
    getComments(vId)
      .then(setComments)
      .catch(() => {})
      .finally(() => setCommentsLoading(false))
  }

  const handleVersionSwitch = (vId: string) => {
    setSearchParams({ version: vId })
  }

  const handleApprove = async (approved: boolean) => {
    if (!id || !versionId) return
    setSubmitting(true)
    try {
      await approveVersion(id, versionId, approved)
      const [updatedApprovals, updatedVersion] = await Promise.all([
        getVersionApprovals(id, versionId),
        getArticleVersionById(id, versionId),
      ])
      setApprovals(updatedApprovals)
      setVersion(updatedVersion)
      setDone(true)
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    } finally {
      setSubmitting(false)
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

  if (error) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <p className="text-destructive">{error}</p>
          <Button variant="outline" onClick={() => navigate(`/articles/${id}`)}>Вернуться к статье</Button>
        </div>
      </div>
    )
  }

  if (!article || !user) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center text-muted-foreground">Нет данных</div>
      </div>
    )
  }

  const currentVersion = version

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="flex-1 max-w-3xl w-full mx-auto px-4 py-8 space-y-8">
        <div>
          <Link to={`/articles/${id}`} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            &larr; Назад к статье
          </Link>
          <h1 className="text-2xl font-bold tracking-tight mt-2">
            Версия {currentVersion?.version_number}
            {currentVersion && (
              <span className={`ml-2 rounded-full px-2 py-0.5 text-sm font-medium ${
                currentVersion.status === 'DRAFT' ? 'bg-gray-100 text-gray-700' :
                currentVersion.status === 'REVIEW' ? 'bg-blue-100 text-blue-700' :
                currentVersion.status === 'PUBLISHED' ? 'bg-green-100 text-green-700' :
                currentVersion.status === 'PENDING_APPROVAL' ? 'bg-amber-100 text-amber-700' :
                currentVersion.status === 'REJECTED' ? 'bg-red-100 text-red-700' :
                ''
              }`}>
                {currentVersion.status === 'DRAFT' ? 'Черновик' :
                 currentVersion.status === 'REVIEW' ? 'На рецензии' :
                 currentVersion.status === 'PUBLISHED' ? 'Опубликована' :
                 currentVersion.status === 'PENDING_APPROVAL' ? 'На согласовании' :
                 currentVersion.status === 'REJECTED' ? 'Отклонена' :
                 currentVersion.status}
              </span>
            )}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Статья: {article.title}
          </p>
        </div>

        {/* Version selector */}
        {versionsList.length > 1 && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-muted-foreground">Версии:</span>
            {versionsList.map((v) => (
              <button
                key={v.id}
                onClick={() => handleVersionSwitch(v.id)}
                className={`rounded-full px-3 py-1 text-xs border transition-colors ${
                  v.id === versionId
                    ? 'border-primary bg-primary/10 text-primary font-medium'
                    : 'border-border text-muted-foreground hover:border-foreground'
                }`}
              >
                #{v.version_number}
              </button>
            ))}
          </div>
        )}

        {/* Version content */}
        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Содержимое версии</h2>
          {versionLoading ? (
            <p className="text-sm text-muted-foreground">Загрузка версии...</p>
          ) : currentVersion ? (
            <div className="space-y-4">
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Название</label>
                <p className="text-lg font-medium">{currentVersion.title}</p>
              </div>
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Аннотация</label>
                <p className="text-sm leading-relaxed">{currentVersion.abstract || '—'}</p>
              </div>
              {currentVersion.keywords.length > 0 && (
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Ключевые слова</label>
                  <div className="flex flex-wrap gap-2">
                    {currentVersion.keywords.map((kw) => (
                      <span key={kw} className="rounded-full border px-3 py-1 text-xs text-muted-foreground">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Язык</label>
                <p className="text-sm">{currentVersion.language.toUpperCase()}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Не удалось загрузить версию</p>
          )}
        </section>

        {/* Review decision */}
        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Рецензирование</h2>
          {reviewLoading ? (
            <p className="text-sm text-muted-foreground">Загрузка...</p>
          ) : review ? (
            <div className="space-y-3">
              <div className={`rounded-lg border px-4 py-3 ${
                review.status === 'APPROVED' ? 'border-green-200 bg-green-50' :
                review.status === 'REJECTED' ? 'border-red-200 bg-red-50' :
                'border-amber-200 bg-amber-50'
              }`}>
                <p className={`text-sm font-medium ${reviewStatusColors[review.status] || ''}`}>
                  Рецензия: {reviewStatusLabels[review.status] || review.status}
                </p>
                {review.completed_at && (
                  <p className="text-xs text-muted-foreground mt-1">
                    {new Date(review.completed_at).toLocaleDateString('ru-RU')}
                  </p>
                )}
              </div>

              {/* Comments from reviewer */}
              {commentsLoading ? (
                <p className="text-sm text-muted-foreground">Загрузка комментариев...</p>
              ) : comments.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Комментарии рецензента</p>
                  {comments.map((c) => (
                    <div key={c.id} className="rounded-lg border px-3 py-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium">{c.user_name || 'Пользователь'}</span>
                        <span className="text-xs text-muted-foreground">
                          {new Date(c.created_at).toLocaleString('ru-RU')}
                        </span>
                      </div>
                      <p className="text-sm">{c.content}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">Нет комментариев рецензента</p>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Рецензия ещё не проведена</p>
          )}
        </section>

        {/* Co-author approvals */}
        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Согласование соавторов</h2>
          {approvalsLoading ? (
            <p className="text-sm text-muted-foreground">Загрузка...</p>
          ) : approvals.length === 0 ? (
            <p className="text-sm text-muted-foreground">Нет данных</p>
          ) : (
            <div className="space-y-2">
              {approvals.map((a) => (
                <div key={a.id} className="flex items-center justify-between rounded-lg border px-3 py-2">
                  <span className="text-sm">{a.approver_name}</span>
                  <span className={`text-xs font-medium ${statusColors[a.status] || ''}`}>
                    {statusLabels[a.status] || a.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Approval actions for co-authors */}
        {version?.status === 'PENDING_APPROVAL' && canApprove && myApproval?.status === 'PENDING' && !done && (
          <section className="rounded-lg border p-4">
            <h2 className="text-lg font-semibold mb-3">Ваше решение</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Ознакомьтесь с содержимым версии выше и примите решение.
            </p>
            <div className="flex items-center gap-2">
              <Button onClick={() => handleApprove(true)} disabled={submitting}>
                {submitting ? 'Отправка...' : 'Одобрить'}
              </Button>
              <Button variant="outline" onClick={() => handleApprove(false)} disabled={submitting}>
                {submitting ? 'Отправка...' : 'Отклонить'}
              </Button>
            </div>
          </section>
        )}

        {done && (
          <p className="text-sm text-muted-foreground text-center">
            {myApproval?.status === 'APPROVED' ? 'Версия одобрена' : 'Решение отправлено'}
          </p>
        )}

        {myApproval && myApproval.status !== 'PENDING' && !done && (
          <p className="text-sm text-muted-foreground text-center">
            Вы уже {myApproval.status === 'APPROVED' ? 'одобрили' : 'отклонили'} эту версию
          </p>
        )}
      </div>
    </div>
  )
}
