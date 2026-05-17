import { useState, useEffect, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { useAuth } from '@/app/providers/AuthProvider'
import { createAuthorProfile, createReviewerProfile } from '@/entities/auth/api'
import { getArticles } from '@/entities/article/api'
import type { CreateAuthorProfileData, CreateReviewerProfileData } from '@/entities/auth/types'
import type { ArticlePayload } from '@/entities/article/types'

const statusLabels: Record<string, string> = {
  DRAFT: 'Черновик',
  PENDING_APPROVAL: 'На согласовании',
  REVIEW: 'На рецензии',
  PUBLISHED: 'Опубликована',
  REJECTED: 'Отклонена',
}

const statusColors: Record<string, string> = {
  DRAFT: 'text-yellow-600',
  PENDING_APPROVAL: 'text-blue-600',
  REVIEW: 'text-purple-600',
  PUBLISHED: 'text-green-600',
  REJECTED: 'text-red-600',
}

export function ProfilePage() {
  const { user, tryLoadUser } = useAuth()
  const navigate = useNavigate()
  const [tab, setTab] = useState<'overview' | 'articles'>('overview')
  const [articles, setArticles] = useState<ArticlePayload[]>([])

  useEffect(() => {
    if (!user) return
    getArticles({ author_id: user.id }).then(setArticles)
  }, [user])

  if (!user) return <Navigate to="/login" replace />

  const hasAuthor = !!user.author_profile
  const hasReviewer = !!user.reviewer_profile
  const initials = user.full_name
    .split(' ')
    .map((s) => s[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="min-h-svh flex flex-col">
      <Header />

      <div className="container mx-auto px-4 py-8 flex-1">
        <div className="flex flex-col md:flex-row gap-8">
          {/* ── sidebar ─────────────────────── */}
          <aside className="md:w-72 shrink-0">
            <div className="flex md:flex-col items-center md:items-start gap-4 md:gap-3">
              <div className="w-16 h-16 md:w-[120px] md:h-[120px] rounded-full bg-muted flex items-center justify-center text-xl md:text-4xl font-bold text-muted-foreground shrink-0">
                {initials}
              </div>
              <div className="text-center md:text-left">
                <h1 className="text-xl md:text-2xl font-bold">{user.full_name}</h1>
                <p className="text-sm text-muted-foreground">{user.username}</p>
              </div>
            </div>

            {user.author_profile?.bio && (
              <p className="text-sm mt-4 text-center md:text-left">{user.author_profile.bio}</p>
            )}

            <div className="space-y-2 mt-4 text-sm text-muted-foreground">
              {user.author_profile?.organization && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span>{user.author_profile.organization}</span>
                </div>
              )}
              {user.author_profile?.position && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span>{user.author_profile.position}</span>
                </div>
              )}
              {user.author_profile?.orcid && (
                <div className="flex items-center gap-2 justify-center md:justify-start">
                  <span>{user.author_profile.orcid}</span>
                </div>
              )}
            </div>

            {/* ── stats ─────────────────────── */}
            <div className="flex gap-4 mt-6 text-sm justify-center md:justify-start">
              <button onClick={() => setTab('articles')} className="hover:text-foreground transition-colors">
                <span className="font-bold">{articles.length}</span>{' '}
                <span className="text-muted-foreground">статей</span>
              </button>
            </div>
          </aside>

          {/* ── main content ────────────────── */}
          <main className="flex-1 min-w-0">
            {/* tabs */}
            <div className="border-b flex gap-6 mb-6">
              <TabButton active={tab === 'overview'} onClick={() => setTab('overview')}>Обзор</TabButton>
              <TabButton active={tab === 'articles'} onClick={() => setTab('articles')}>
                Статьи <span className="text-muted-foreground font-normal">{articles.length}</span>
              </TabButton>
            </div>

            {tab === 'overview' && (
              <div className="space-y-6">
                {/* author profile */}
                {hasAuthor ? (
                  <div className="rounded-xl border p-5">
                    <h2 className="font-semibold mb-3">Профиль автора</h2>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {user.author_profile?.organization && (
                        <div><span className="text-muted-foreground">Организация</span><p className="font-medium">{user.author_profile.organization}</p></div>
                      )}
                      {user.author_profile?.position && (
                        <div><span className="text-muted-foreground">Должность</span><p className="font-medium">{user.author_profile.position}</p></div>
                      )}
                      {user.author_profile?.degree && (
                        <div><span className="text-muted-foreground">Степень</span><p className="font-medium">{user.author_profile.degree}</p></div>
                      )}
                      {user.author_profile?.orcid && (
                        <div><span className="text-muted-foreground">ORCID</span><p className="font-medium">{user.author_profile.orcid}</p></div>
                      )}
                    </div>
                  </div>
                ) : (
                  <CreateProfileBlock
                    title="Профиль автора"
                    description="Расскажите о своей научной деятельности"
                    buttonText="Создать профиль автора"
                    onSubmit={async (data) => {
                      await createAuthorProfile(user.id, data as CreateAuthorProfileData)
                      await tryLoadUser()
                    }}
                    fields={[
                      { key: 'organization', label: 'Организация' },
                      { key: 'position', label: 'Должность' },
                      { key: 'degree', label: 'Степень' },
                      { key: 'orcid', label: 'ORCID', required: true },
                      { key: 'bio', label: 'Био', multiline: true },
                    ]}
                  />
                )}

                {/* reviewer profile */}
                {hasReviewer ? (
                  <div className="rounded-xl border p-5">
                    <h2 className="font-semibold mb-3">Профиль рецензента</h2>
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      {user.reviewer_profile?.specialization && (
                        <div><span className="text-muted-foreground">Специализация</span><p className="font-medium">{user.reviewer_profile.specialization}</p></div>
                      )}
                      {user.reviewer_profile?.degree && (
                        <div><span className="text-muted-foreground">Степень</span><p className="font-medium">{user.reviewer_profile.degree}</p></div>
                      )}
                    </div>
                  </div>
                ) : (
                  <CreateProfileBlock
                    title="Профиль рецензента"
                    description="Станьте рецензентом научных статей"
                    buttonText="Создать профиль рецензента"
                    onSubmit={async (data) => {
                      await createReviewerProfile(user.id, data as CreateReviewerProfileData)
                      await tryLoadUser()
                    }}
                    fields={[
                      { key: 'specialization', label: 'Специализация', required: true },
                      { key: 'degree', label: 'Степень' },
                    ]}
                  />
                )}
              </div>
            )}

            {tab === 'articles' && (
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
                          {a.updated_at && (
                            <span>Обновлено {new Date(a.updated_at).toLocaleDateString('ru-RU')}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                {articles.length === 0 && (
                  <p className="text-sm text-muted-foreground py-8 text-center">Статей пока нет</p>
                )}
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}

function TabButton({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`pb-3 text-sm font-medium border-b-2 transition-colors ${
        active ? 'border-foreground text-foreground' : 'border-transparent text-muted-foreground hover:text-foreground'
      }`}
    >
      {children}
    </button>
  )
}

type FieldDef = {
  key: string
  label: string
  multiline?: boolean
  required?: boolean
}

function CreateProfileBlock({
  title,
  description,
  buttonText,
  onSubmit,
  fields,
}: {
  title: string
  description: string
  buttonText: string
  onSubmit: (data: Record<string, string>) => Promise<void>
  fields: FieldDef[]
}) {
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!open) {
    return (
      <div className="rounded-xl border border-dashed p-5">
        <h2 className="font-semibold mb-1">{title}</h2>
        <p className="text-sm text-muted-foreground mb-3">{description}</p>
        <Button size="sm" onClick={() => setOpen(true)}>{buttonText}</Button>
      </div>
    )
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    const requiredMissing = fields.filter((f) => f.required && !formData[f.key]?.trim())
    if (requiredMissing.length > 0) {
      setError(`Заполните обязательные поля: ${requiredMissing.map((f) => f.label).join(', ')}`)
      return
    }

    setPending(true)
    try {
      const data: Record<string, string> = {}
      for (const f of fields) {
        if (formData[f.key]) data[f.key] = formData[f.key]
      }
      await onSubmit(data)
      setOpen(false)
    } catch (e: any) {
      setError(e.message ?? 'Ошибка')
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="rounded-xl border p-5">
      <h2 className="font-semibold mb-3">{title}</h2>
      <form onSubmit={handleSubmit} className="space-y-3">
        {fields.map((f) =>
          f.multiline ? (
            <div key={f.key}>
              <label className="text-sm font-medium mb-1 block">
                {f.label}{f.required && <span className="text-destructive ml-0.5">*</span>}
              </label>
              <textarea
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[80px] resize-y"
                value={formData[f.key] ?? ''}
                onChange={(e) => setFormData((p) => ({ ...p, [f.key]: e.target.value }))}
              />
            </div>
          ) : (
            <div key={f.key}>
              <label className="text-sm font-medium mb-1 block">
                {f.label}{f.required && <span className="text-destructive ml-0.5">*</span>}
              </label>
              <input
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={formData[f.key] ?? ''}
                onChange={(e) => setFormData((p) => ({ ...p, [f.key]: e.target.value }))}
                required={f.required}
              />
            </div>
          ),
        )}
        {error && <p className="text-sm text-destructive">{error}</p>}
        <div className="flex items-center gap-3">
          <Button type="submit" disabled={pending} size="sm">{pending ? 'Сохранение...' : 'Сохранить'}</Button>
          <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>Отмена</Button>
        </div>
      </form>
    </div>
  )
}
