import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { getArticle, updateArticle } from '@/entities/article/api'
import { getJournals } from '@/entities/journal/api'
import type { ArticleFullPayload } from '@/entities/article/types'
import type { JournalPayload } from '@/entities/journal/types'

export function EditArticlePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [article, setArticle] = useState<ArticleFullPayload | null>(null)
  const [journals, setJournals] = useState<JournalPayload[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [keywords, setKeywords] = useState('')
  const [language, setLanguage] = useState('en')
  const [journalId, setJournalId] = useState('')

  useEffect(() => {
    if (!id) return
    Promise.all([
      getArticle(id),
      getJournals(),
    ])
      .then(([art, jls]) => {
        setArticle(art)
        setJournals(jls)
        setTitle(art.title)
        setAbstract(art.abstract ?? '')
        setKeywords(art.keywords.join(', '))
        setLanguage(art.language)
        setJournalId(art.journal_id ?? '')
      })
      .catch((e: any) => setError(e.message ?? 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [id])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!id) return
    setSaving(true)
    setError(null)
    try {
      const parsed = keywords
        .split(/[;,]/)
        .map((k) => k.trim())
        .filter(Boolean)
      await updateArticle(id, {
        title,
        abstract: abstract || null,
        keywords: parsed,
        language,
        journal_id: journalId || null,
      })
      navigate(`/articles/${id}`)
    } catch (e: any) {
      setError(e.message ?? 'Ошибка')
    } finally {
      setSaving(false)
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

  if (error && !article) {
    return (
      <div className="min-h-svh flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center text-muted-foreground">{error}</div>
      </div>
    )
  }

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 flex-1 max-w-2xl">
        <h1 className="text-2xl font-bold tracking-tight mb-6">Редактировать статью</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">Название *</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Аннотация</label>
            <textarea
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[100px] resize-y"
              value={abstract}
              onChange={(e) => setAbstract(e.target.value)}
            />
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Ключевые слова (через запятую)</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={keywords}
              onChange={(e) => setKeywords(e.target.value)}
              placeholder="keyword1, keyword2"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Язык</label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="ru">Русский</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Журнал</label>
              <select
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={journalId}
                onChange={(e) => setJournalId(e.target.value)}
              >
                <option value="">Без журнала</option>
                {journals.map((j) => (
                  <option key={j.id} value={j.id}>{j.name}</option>
                ))}
              </select>
            </div>
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <div className="flex items-center gap-3 pt-2">
            <Button type="submit" disabled={saving}>
              {saving ? 'Сохранение...' : 'Сохранить'}
            </Button>
            <Button type="button" variant="ghost" onClick={() => navigate(`/articles/${id}`)}>
              Отмена
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
