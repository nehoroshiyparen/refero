import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import {
  getReviewAssignment,
  getReviewByAssignment,
  submitReview,
  getComments,
  addComment,
} from '@/entities/review'
import { getArticleVersionById } from '@/entities/article/api'
import type { ReviewAssignmentFullPayload, ReviewPayload, CommentPayload } from '@/entities/review/types'
import type { ArticleVersionPayload } from '@/entities/article/types'

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

export function AssignmentReviewPage() {
  const { assignmentId } = useParams<{ assignmentId: string }>()
  const navigate = useNavigate()
  const { user } = useAuth()

  const [assignment, setAssignment] = useState<ReviewAssignmentFullPayload | null>(null)
  const [review, setReview] = useState<ReviewPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [version, setVersion] = useState<ArticleVersionPayload | null>(null)
  const [versionLoading, setVersionLoading] = useState(false)

  const [comments, setComments] = useState<CommentPayload[]>([])
  const [commentsLoading, setCommentsLoading] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [commentSubmitting, setCommentSubmitting] = useState(false)

  const [submittingReview, setSubmittingReview] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  useEffect(() => {
    if (!assignmentId || !user) return
    setLoading(true)

    Promise.all([
      getReviewAssignment(assignmentId),
      getReviewByAssignment(assignmentId),
    ])
      .then(([a, r]) => {
        if (!a) {
          setError('Назначение не найдено')
          return
        }
        setAssignment(a)
        setReview(r)

        if (a.article_version_id) {
          setVersionLoading(true)
          getArticleVersionById(a.article_id!, a.article_version_id)
            .then(setVersion)
            .catch(() => {})
            .finally(() => setVersionLoading(false))

          setCommentsLoading(true)
          getComments(a.article_version_id)
            .then(setComments)
            .catch(() => {})
            .finally(() => setCommentsLoading(false))
        }
      })
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [assignmentId, user])

  const handleSubmit = async (status: 'APPROVED' | 'REJECTED' | 'REQUESTING_CHANGES') => {
    if (!assignmentId) return
    setSubmittingReview(true)
    try {
      const result = await submitReview(assignmentId, status)
      setReview(result)
      setSubmitted(true)
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    } finally {
      setSubmittingReview(false)
    }
  }

  const handleAddComment = async () => {
    if (!assignment?.article_version_id || !newComment.trim()) return
    setCommentSubmitting(true)
    try {
      const result = await addComment(assignment.article_version_id, newComment.trim())
      setComments([...comments, result])
      setNewComment('')
    } catch (e: any) {
      alert(e.message ?? 'Ошибка')
    } finally {
      setCommentSubmitting(false)
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

  if (error || !assignment) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <p className="text-destructive">{error ?? 'Назначение не найдено'}</p>
          <Button variant="outline" onClick={() => navigate('/reviews/assignments')}>К назначениям</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="flex-1 max-w-3xl w-full mx-auto px-4 py-8 space-y-8">
        <div>
          <Link to="/reviews/assignments" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            &larr; К назначениям
          </Link>
          <h1 className="text-2xl font-bold tracking-tight mt-2">
            {assignment.article_title || 'Без названия'}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Версия {assignment.version_number}
            {assignment.version_title && <> &mdash; {assignment.version_title}</>}
          </p>
        </div>

        {review && (
          <div className={`rounded-lg border px-4 py-3 ${review.status === 'APPROVED' ? 'border-green-200 bg-green-50' : review.status === 'REJECTED' ? 'border-red-200 bg-red-50' : 'border-amber-200 bg-amber-50'}`}>
            <p className={`text-sm font-medium ${reviewStatusColors[review.status] || ''}`}>
              Ревью завершено — {reviewStatusLabels[review.status] || review.status}
            </p>
            {review.completed_at && (
              <p className="text-xs text-muted-foreground mt-1">
                {new Date(review.completed_at).toLocaleDateString('ru-RU')}
              </p>
            )}
          </div>
        )}

        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Содержимое версии</h2>
          {versionLoading ? (
            <p className="text-sm text-muted-foreground">Загрузка...</p>
          ) : version ? (
            <div className="space-y-4">
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Название</label>
                <p className="text-lg font-medium">{version.title}</p>
              </div>
              {version.abstract && (
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Аннотация</label>
                  <p className="text-sm leading-relaxed">{version.abstract}</p>
                </div>
              )}
              {version.keywords.length > 0 && (
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Ключевые слова</label>
                  <div className="flex flex-wrap gap-2">
                    {version.keywords.map((kw) => (
                      <span key={kw} className="rounded-full border px-3 py-1 text-xs text-muted-foreground">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Язык</label>
                <p className="text-sm">{version.language.toUpperCase()}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Не удалось загрузить версию</p>
          )}
        </section>

        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Комментарии</h2>
          {commentsLoading ? (
            <p className="text-sm text-muted-foreground">Загрузка...</p>
          ) : (
            <div className="space-y-3 mb-4">
              {comments.length === 0 && (
                <p className="text-sm text-muted-foreground">Нет комментариев</p>
              )}
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
          )}

          {!review && (
            <div className="flex items-start gap-2">
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Напишите комментарий..."
                rows={2}
                className="flex-1 rounded-lg border px-3 py-2 text-sm resize-none"
              />
              <Button
                size="sm"
                onClick={handleAddComment}
                disabled={commentSubmitting || !newComment.trim()}
              >
                {commentSubmitting ? '...' : 'Отправить'}
              </Button>
            </div>
          )}
        </section>

        {!review && !submitted && (
          <section className="rounded-lg border p-4">
            <h2 className="text-lg font-semibold mb-3">Решение</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Ознакомьтесь с содержимым версии и комментариями, затем вынесите решение.
            </p>
            <div className="flex flex-wrap items-center gap-2">
              <Button onClick={() => handleSubmit('APPROVED')} disabled={submittingReview}>
                {submittingReview ? 'Отправка...' : 'Одобрить'}
              </Button>
              <Button variant="outline" onClick={() => handleSubmit('REQUESTING_CHANGES')} disabled={submittingReview}>
                Запросить изменения
              </Button>
              <Button variant="outline" onClick={() => handleSubmit('REJECTED')} disabled={submittingReview} className="text-destructive">
                Отклонить
              </Button>
            </div>
          </section>
        )}

        {submitted && (
          <p className="text-sm text-muted-foreground text-center">
            Решение отправлено
          </p>
        )}
      </div>
    </div>
  )
}
