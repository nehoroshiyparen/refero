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
import type { ArticleFullPayload, ArticleVersionPayload, ApprovalBrief } from '@/entities/article/types'

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

export function ReviewPage() {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
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

  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  const isCoAuthor = user && article?.authors.some((a) => a.author_id === user.id)
  const myApproval = approvals.find((a) => a.approver_id === user?.id)

  useEffect(() => {
    if (!id) return
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
              setError('Не указана версия для рассмотрения')
              return
            }

            setVersionId(targetVersionId)
            setVersionLoading(true)
            getArticleVersionById(id, targetVersionId)
              .then(setVersion)
              .catch(() => setError('Не удалось загрузить версию статьи'))
              .finally(() => setVersionLoading(false))

            setApprovalsLoading(true)
            getVersionApprovals(id, targetVersionId)
              .then(setApprovals)
              .catch(() => {})
              .finally(() => setApprovalsLoading(false))
          })
          .catch(() => setError('Не удалось загрузить версии'))
      })
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [id, versionIdFromUrl])

  const handleApprove = async (approved: boolean) => {
    if (!id || !versionId) return
    setSubmitting(true)
    try {
      await approveVersion(id, versionId, approved)
      setDone(true)
      const updated = await getVersionApprovals(id, versionId)
      setApprovals(updated)
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

  if (!isCoAuthor) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <p className="text-muted-foreground">У вас нет доступа к этой странице</p>
          <Button variant="outline" onClick={() => navigate('/articles')}>К списку статей</Button>
        </div>
      </div>
    )
  }

  const versionToReview = version
  const otherPendingVersions = versionsList.filter(
    (v) => v.status === 'PENDING_APPROVAL' && v.id !== versionToReview?.id
  )

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="flex-1 max-w-3xl w-full mx-auto px-4 py-8 space-y-8">
        <div>
          <Link to={`/articles/${id}`} className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            &larr; Назад к статье
          </Link>
          <h1 className="text-2xl font-bold tracking-tight mt-2">
            Согласование версии
            {versionToReview && <span className="text-muted-foreground"> #{versionToReview.version_number}</span>}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Статья: {article.title}
          </p>
        </div>

        {otherPendingVersions.length > 0 && (
          <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3">
            <p className="text-sm text-amber-800">
              Есть другие версии, ожидающие согласования:{' '}
              {otherPendingVersions.map((v, i) => (
                <span key={v.id}>
                  {i > 0 && ', '}
                  <Link
                    to={`/articles/${id}/review?version=${v.id}`}
                    className="underline font-medium"
                  >
                    версия #{v.version_number}
                  </Link>
                </span>
              ))}
            </p>
          </div>
        )}

        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Содержимое версии</h2>
          {versionLoading ? (
            <p className="text-sm text-muted-foreground">Загрузка версии...</p>
          ) : versionToReview ? (
            <div className="space-y-4">
              <div>
                <span className="text-xs text-muted-foreground">Версия #{versionToReview.version_number}</span>
              </div>
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Название</label>
                <p className="text-lg font-medium">{versionToReview.title}</p>
              </div>
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Аннотация</label>
                <p className="text-sm leading-relaxed">{versionToReview.abstract || '—'}</p>
              </div>
              {versionToReview.keywords.length > 0 && (
                <div>
                  <label className="text-xs text-muted-foreground block mb-1">Ключевые слова</label>
                  <div className="flex flex-wrap gap-2">
                    {versionToReview.keywords.map((kw) => (
                      <span key={kw} className="rounded-full border px-3 py-1 text-xs text-muted-foreground">
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <label className="text-xs text-muted-foreground block mb-1">Язык</label>
                <p className="text-sm">{versionToReview.language.toUpperCase()}</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Не удалось загрузить версию</p>
          )}
        </section>

        <section className="rounded-lg border p-4">
          <h2 className="text-lg font-semibold mb-4">Статусы согласования</h2>
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

        {myApproval?.status === 'PENDING' && !done && (
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
