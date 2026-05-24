import { useState, useEffect, type FormEvent } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'
import { createArticle } from '@/entities/article/api'
import { getJournals } from '@/entities/journal/api'
import type { JournalPayload } from '@/entities/journal/types'

export function CreateArticlePage() {
  const navigate = useNavigate()
  const [journals, setJournals] = useState<JournalPayload[]>([])
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [keywordsStr, setKeywordsStr] = useState('')
  const [language, setLanguage] = useState('en')
  const [journalId, setJournalId] = useState('')
  const [pending, setPending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getJournals().then(setJournals)
  }, [])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)
    setPending(true)
    try {
      const keywords = keywordsStr
        .split(/[,;]/)
        .map((s) => s.trim())
        .filter(Boolean)
      await createArticle({
        title,
        abstract: abstract || undefined,
        keywords: keywords.length > 0 ? keywords : undefined,
        language,
        pdf_path: '',
        journal_id: journalId || undefined,
      })
      navigate('/articles')
    } catch (e: any) {
      setError(e.message ?? 'Ошибка создания')
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="min-h-svh flex flex-col">
      <Header />
      <div className="container mx-auto px-4 py-8 flex-1 max-w-2xl">
        <div className="mb-6">
          <Link to="/articles" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            &larr; Назад к статьям
          </Link>
          <h1 className="text-2xl font-bold tracking-tight mt-2">Новая статья</h1>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
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
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm min-h-[120px] resize-y"
              value={abstract}
              onChange={(e) => setAbstract(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Язык</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="en">English</option>
                <option value="ru">Русский</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Журнал</label>
              <select
                value={journalId}
                onChange={(e) => setJournalId(e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="">Без журнала</option>
                {journals.map((j) => (
                  <option key={j.id} value={j.id}>{j.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block">Ключевые слова</label>
            <input
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={keywordsStr}
              onChange={(e) => setKeywordsStr(e.target.value)}
              placeholder="через запятую или точку с запятой"
            />
          </div>

          {error && <p className="text-sm text-destructive">{error}</p>}

          <div className="flex items-center gap-3 pt-2">
            <Button type="submit" disabled={pending}>
              {pending ? 'Создание...' : 'Создать'}
            </Button>
            <Button type="button" variant="outline" onClick={() => navigate('/articles')}>
              Отмена
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}
