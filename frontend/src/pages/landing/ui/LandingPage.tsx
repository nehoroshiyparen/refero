import { Header } from '@/shared/ui/header'
import { Button } from '@/shared/ui/button'

const features = [
  {
    title: 'Управление статьями',
    description: 'Полный жизненный цикл: черновик, согласование с соавторами, рецензирование и публикация. Фильтрация по статусу, журналу, языку, автору и ключевым словам.',
  },
  {
    title: 'Рецензирование',
    description: 'Структурированный процесс рецензирования со статусами PENDING, APPROVED, REJECTED и REQUESTING_CHANGES. Прозрачность для авторов и рецензентов.',
  },
  {
    title: 'Совместная работа',
    description: 'Добавляйте соавторов, отправляйте статью на согласование и отслеживайте, кто подтвердил или отклонил текущую версию.',
  },
  {
    title: 'Аутентификация и роли',
    description: 'JWT-авторизация с httpOnly куками. Три роли: AUTHOR, REVIEWER и ADMIN — каждая с разграничением доступа.',
  },
  {
    title: 'Журналы',
    description: 'Управление научными журналами через администратора. Группировка статей по тематическим направлениям.',
  },
  {
    title: 'Цитирования',
    description: 'Встроенный модуль отслеживания цитируемости статей внутри платформы.',
  },
]

const workflowSteps = [
  { label: 'Черновик', description: 'Создание и редактирование метаданных, загрузка PDF, добавление соавторов' },
  { label: 'Согласование', description: 'Каждый соавтор подтверждает или отклоняет текущую версию статьи' },
  { label: 'Рецензия', description: 'Рецензенты изучают статью и выносят решение' },
  { label: 'Публикация', description: 'Статья доступна для чтения и цитирования всем пользователям' },
]

const techStack = [
  { category: 'Бэкенд', items: 'Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 16' },
  { category: 'Фронтенд', items: 'React 19, TypeScript 6, Vite, Tailwind CSS' },
  { category: 'Инфраструктура', items: 'Docker, Docker Compose' },
  { category: 'Безопасность', items: 'JWT, bcrypt, httpOnly cookies' },
]

export function LandingPage() {
  return (
    <div className="min-h-svh">
      <Header />

      {/* ── Hero ─────────────────────────────────── */}
      <section className="container mx-auto px-4 pt-24 pb-16 text-center">
        <h1 className="text-5xl sm:text-6xl font-bold tracking-tight mb-6">
          Публикация научных
          <span className="text-primary block mt-2">статей без боли</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10">
          Refero управляет полным циклом научной публикации — от черновика и совместной
          работы с соавторами до рецензирования и финальной публикации.
        </p>
        <div className="flex items-center justify-center gap-4">
          <a href="/register">
            <Button size="lg">Начать работу</Button>
          </a>
          <a href="#features">
            <Button variant="outline" size="lg">Подробнее</Button>
          </a>
        </div>
      </section>

      {/* ── Features ─────────────────────────────── */}
      <section id="features" className="border-t py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-12">
            Всё необходимое для публикации
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className="rounded-xl border p-6 hover:shadow-md transition-shadow"
              >
                <h3 className="font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Workflow ─────────────────────────────── */}
      <section id="workflow" className="border-t py-20 bg-muted/30">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-4">
            Процесс публикации
          </h2>
          <p className="text-muted-foreground text-center max-w-xl mx-auto mb-12">
            Каждая статья проходит структурированный конвейер от создания до публикации.
          </p>
          <div className="grid sm:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {workflowSteps.map((step, i) => (
              <div key={step.label} className="relative text-center">
                <div className="rounded-full bg-primary text-primary-foreground w-10 h-10 flex items-center justify-center mx-auto mb-3 text-sm font-bold">
                  {i + 1}
                </div>
                <h3 className="font-semibold text-sm mb-1">{step.label}</h3>
                <p className="text-xs text-muted-foreground">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Tech Stack ───────────────────────────── */}
      <section id="tech-stack" className="border-t py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold tracking-tight text-center mb-12">
            Технологии
          </h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {techStack.map((t) => (
              <div key={t.category} className="rounded-xl border p-5 text-center">
                <h3 className="font-semibold text-sm text-muted-foreground mb-2 uppercase tracking-wide">
                  {t.category}
                </h3>
                <p className="text-sm">{t.items}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────── */}
      <footer className="border-t py-8 text-center text-sm text-muted-foreground">
        <div className="container mx-auto px-4">
          <p>&copy; {new Date().getFullYear()} Refero. Open source.</p>
        </div>
      </footer>
    </div>
  )
}
