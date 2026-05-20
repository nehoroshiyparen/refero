import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { getReviewAssignments } from '@/entities/review'
import type { ReviewAssignmentFullPayload } from '@/entities/review/types'

const statusColors: Record<string, string> = {
  APPROVED: 'text-green-600',
  REJECTED: 'text-red-600',
  REQUESTING_CHANGES: 'text-amber-600',
}

const statusLabels: Record<string, string> = {
  APPROVED: 'Одобрена',
  REJECTED: 'Отклонена',
  REQUESTING_CHANGES: 'Запрошены изменения',
}

export function AssignmentsPage() {
  const navigate = useNavigate()

  const [assignments, setAssignments] = useState<ReviewAssignmentFullPayload[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getReviewAssignments()
      .then(setAssignments)
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [])

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
          <Button variant="outline" onClick={() => navigate('/')}>На главную</Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold tracking-tight mb-6">Мои рецензии</h1>

        {assignments.length === 0 ? (
          <p className="text-muted-foreground">Нет назначений</p>
        ) : (
          <div className="space-y-3">
            {assignments.map((a) => (
              <div
                key={a.id}
                className="rounded-xl border p-4 flex items-center justify-between cursor-pointer hover:bg-muted/50 transition-colors"
                onClick={() => navigate(`/reviews/assignments/${a.id}`)}
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">{a.article_title || 'Без названия'}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    Версия {a.version_number}
                    {a.version_title && <> &mdash; {a.version_title}</>}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Назначена {new Date(a.created_at).toLocaleDateString('ru-RU')}
                  </p>
                </div>
                <div className="ml-4 shrink-0">
                  {a.review_status ? (
                    <span className={`text-sm font-medium ${statusColors[a.review_status] || ''}`}>
                      {statusLabels[a.review_status] || a.review_status}
                    </span>
                  ) : (
                    <span className="text-sm text-muted-foreground">Ожидает</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
