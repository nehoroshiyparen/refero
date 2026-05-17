# Клиент Refero — план реализации

**API:** 34 эндпоинта, 6 модулей (auth, users, articles, reviews, journals, citations)

---

## Фаза 0 — Архитектура

```
app/
 └ providers/
     ├ AuthProvider.tsx     ← контекст: user, roles, токены
     └ RoleGuard.tsx        ← компонент-обёртка для protected routes
features/
 └ auth/
     ├ useLogin.ts
     ├ useRegister.ts
     ├ useLogout.ts
     ├ useUser.ts
     └ useRequireRole.ts   ← хук: проверяет роль и редиректит
```

Роли: `AUTHOR`, `REVIEWER`, `ADMIN`

---

## Фаза 1 — Фундамент (Auth + API)

**Страницы:**
- `/login` — вход (email/username + password)
- `/register` — регистрация (username, email, full_name, password)

**Что сделать:**
- `shared/api/client.ts` — fetch-обёртка с Bearer-токеном, авто-refresh на 401
- `entities/auth/types.ts` — AccessTokenPayload, AuthTokens
- `entities/auth/api/` — login(), register(), logout(), refresh()
- `app/providers/AuthProvider.tsx` — хранит пользователя (/api/users/me при загрузке)
- `app/routes/` — защищённые роуты (redirect на /login)

---

## Фаза 2 — Статьи (CRUD + список)

**Страницы:**
- `/articles` — список c фильтрацией (поиск, статус, журнал, язык)
- `/articles/new` — создание
- `/articles/:id` — просмотр (авторы, версии, цитирования)
- `/articles/:id/edit` — редактирование

**Что сделать:**
- `entities/article/types.ts` — Article, ArticleFull, ArticleVersion, ArticleStatus
- `entities/article/api/` — getArticles(), getArticle(), createArticle(), updateArticle(), deleteArticle(), downloadPdf()
- `features/article/useArticleList.ts` — пагинация + фильтры
- `features/article/useCreateArticle.ts`, useUpdateArticle.ts
- `shared/ui/Pagination.tsx`, `shared/ui/FilterBar.tsx`

---

## Фаза 3 — Соавторы + Версионность

**На странице статьи:**
- Блок соавторов: добавить/удалить
- Список версий: создать новую, удалить старую
- Кнопка «Отправить на согласование»

**Что сделать:**
- `entities/article/api/` — addAuthor(), removeAuthor(), createVersion(), deleteVersion(), submitForApproval()
- `features/article/useAuthors.ts`, useVersions.ts, useSubmitForApproval.ts

---

## Фаза 4 — Согласование + Рецензирование

**Страницы:**
- Голосование соавтора (на странице статьи)
- `/reviews/assignments` — список назначенных рецензий (REVIEWER)
- `/reviews/assignments/:id` — комментарии + решение

**Что сделать:**
- `entities/review/types.ts` — Review, ReviewAssignment, Comment
- `entities/review/api/` — approveVersion(), getAssignments(), submitReview(), getComments(), postComment()
- `features/review/useApproveVersion.ts`, useSubmitReview.ts, useComments.ts

---

## Фаза 5 — Профиль + Админка

**Страницы:**
- `/profile` — редактирование, создание профиля автора/рецензента
- `/admin/journals` (ADMIN) — CRUD журналов
- `/admin/users` (ADMIN) — список пользователей

**Что сделать:**
- `entities/user/api/` — getMe(), updateProfile(), createAuthorProfile(), createReviewerProfile(), getUsers()
- `features/user/useProfile.ts`
- `features/journal/useJournal.ts`

---

## Фаза 6 — Доработки

- Цитирования на странице статьи
- Лоадеры, скелетоны, error-boundary, toast-уведомления
