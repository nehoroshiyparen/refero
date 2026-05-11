# Plan: Refero Project Structure & Development

## Problem & Approach

Проект SciFlow/Refero — это платформа для управления статьями, рецензирования и авторов. Есть уже инфраструктура (backend, frontend), но нужна структуризация и четкое понимание того, что делать дальше в каждом модуле.

**Подход:**

1. Провести аудит текущего состояния (модели, сервисы, роуты)
2. Выявить неполные модули
3. Составить план разработки для каждого модуля
4. Структурировать задачи в очередь

## Current Architecture

### Backend Structure (FastAPI + SQLAlchemy Async)

- **Core**: конфиг, роуты, обработчики исключений, зависимости
- **Infrastructure**: БД (SQLAlchemy, Alembic миграции)
- **Modules**: бизнес-логика (auth, users, articles, etc.)

### Implemented Modules

1. **Auth** ✅ (service, router, repository, utils для tokens)
   - Register, Login, Logout, Refresh tokens
   - Работает с RefreshToken моделью
2. **Users** ✅ (service, router, repository, query_builder)
   - Модель User с ролями (Role, RoleName enum)
   - Relations: RefreshTokens, AuthorProfile, ReviewerProfile
3. **Authors** ⚠️ (service, repository, query_builder, модель AuthorProfile)
   - Есть структура, но неполная реализация
4. **Reviewers** ⚠️ (service, repository, query_builder, модель ReviewerProfile)
   - Есть структура, но неполная реализация

### Incomplete/Empty Modules

- **Articles** (только service.py пуст)
- **Reviews** (только service.py пуст)
- **Citations** (только service, router, repository)

## Data Models (Finalized)

### 1. **Journals** (Новая таблица)

```
id (UUID, PK)
name (VARCHAR, NOT NULL, UNIQUE)
issn (VARCHAR, nullable)
description (TEXT)
created_at (TIMESTAMP)
```

### 2. **Articles** (Основная таблица статей)

```
id (UUID, PK)
title (TEXT, NOT NULL)
abstract (TEXT)
keywords (TEXT[] или JSON)
language (VARCHAR(5), default='en')
year (SMALLINT)
doi (VARCHAR, nullable, UNIQUE)
pdf_path (VARCHAR, nullable) — путь к загруженному файлу
journal_id (UUID, FK → journals, nullable)
status (ENUM: draft, review, published, rejected)
view_count (INTEGER, default=0)
download_count (INTEGER, default=0)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
updated_by_user_id (UUID, FK → users)
published_at (TIMESTAMP, nullable)
```

### 3. **ArticleAuthors** (Many-to-many связь авторов и статей)

```
id (UUID, PK)
article_id (UUID, FK → articles, ON DELETE CASCADE)
author_id (UUID, FK → users, ON DELETE CASCADE)
created_at (TIMESTAMP)
```

### 4. **ArticleApprovals** (Апрувы от соавторов ДО рецензии)

```
id (UUID, PK)
article_id (UUID, FK → articles)
approver_id (UUID, FK → users — соавтор, который апрувит)
status (ENUM: pending, approved, rejected)
comment (TEXT, nullable)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
approved_at (TIMESTAMP, nullable)
```

### 5. **Reviews** (Рецензии на статьи)

```
id (UUID, PK)
article_id (UUID, FK → articles)
reviewer_id (UUID, FK → users — рецензент)
status (ENUM: pending, approved, rejected, requesting_changes)
comment (TEXT, nullable)
created_at (TIMESTAMP)
updated_at (TIMESTAMP)
completed_at (TIMESTAMP, nullable)
```

### 6. **Citations** (Цитирования между статьями)

```
id (UUID, PK)
from_article_id (UUID, FK → articles — статья, которая цитирует)
to_article_id (UUID, FK → articles — статья, на которую ссылаются)
created_at (TIMESTAMP)
```

---

## Publishing Workflow

```
1. AUTHOR создает статью
   └─ status = "draft"
   └─ добавляет соавторов через ArticleAuthors

2. AUTHOR обновляет статью (multiple updates)
   └─ status = "draft"
   └─ updated_at меняется

3. AUTHOR отправляет на апрув от соавторов
   └─ Создаются ArticleApprovals для всех соавторов (кроме создателя)
   └─ status ArticleApprovals = "pending"
   └─ Соавторы видят заявку на апрув

4. СОАВТОРЫ апрувят (все должны согласиться)
   └─ Когда все соавторы апрувят → article.status = "review"

5. ARTICLE отправляется на рецензию
   └─ Создается Reviews с reviewer_id
   └─ article.status = "review"

6. REVIEWER смотрит и апрувит/отклоняет
   └─ review.status = "approved" или "rejected"
   └─ Если approved → article.status = "published"
   └─ Если rejected → article.status = "draft" (можно исправить и заново)

7. ARTICLE опубликована
   └─ article.status = "published"
   └─ article.published_at = now()
```

---

## Tasks

### Phase 1: Create Data Models

- [ ] `models/journals.py` — Journal модель
- [ ] `models/articles.py` — Article модель (с все полями)
- [ ] `models/article_authors.py` — ArticleAuthors (many-to-many)
- [ ] `models/article_approvals.py` — ArticleApprovals (workflow)
- [ ] `models/reviews.py` — Reviews (рецензии)
- [ ] `models/citations.py` — Citations
- [ ] Регистрация всех моделей в `import_models.py`
- [ ] Создать Alembic миграцию для новых таблиц

### Phase 2: Implement Articles Module

- [ ] `modules/articles/repository.py` — CRUD операции
- [ ] `modules/articles/query_builder.py` — фильтрация (по статусу, году, журналу, etc.)
- [ ] `modules/articles/service.py` — бизнес-логика (создание, обновление, статус-переходы)
- [ ] `modules/articles/router.py` — API endpoints

### Phase 3: Implement Approvals & Reviews Workflow

- [ ] `modules/approvals/service.py` — логика апрувов от соавторов
- [ ] `modules/reviews/service.py` — логика рецензирования
- [ ] `modules/reviews/router.py` — API для рецензентов

### Phase 4: Complete Other Modules

- [ ] Authors module (доделать service + router)
- [ ] Reviewers module (доделать service + router)
- [ ] Citations (router + service полностью)
- [ ] Journals (simple CRUD)

### Phase 5: Frontend Integration

- [ ] Analyze frontend structure
- [ ] Connect to backend API

---

## Key Decisions

✅ **Hard delete** для статей (простая логика)
✅ **Many-to-many** авторов без position (просто связь)
✅ **Soft approval workflow** — авторы апрувят перед рецензией
✅ **Reviews отдельно** от approvals (разные этапы)
✅ Async/await SQLAlchemy
✅ Repository + Service + Router pattern
✅ Role-based access (AUTHOR, REVIEWER, ADMIN)

---

## Implementation Order (Dependency)

1. **Models** (всегда первые) → 2. **Repositories** → 3. **Services** → 4. **Routes**

---

## API Endpoints по модулям

### 1. **Articles** endpoints
- `POST /api/articles` — создать новую статью (автор)
- `GET /api/articles` — получить список (с фильтрацией по статусу, году, журналу)
- `GET /api/articles/{id}` — получить статью по ID (увеличить view_count)
- `PUT /api/articles/{id}` — обновить статью (только автор/соавторы, пока draft)
- `DELETE /api/articles/{id}` — удалить статью (только автор, пока draft)
- `POST /api/articles/{id}/submit-for-approval` — отправить на апрув от соавторов
- `GET /api/articles/{id}/authors` — получить авторов статьи
- `POST /api/articles/{id}/authors` — добавить автора (соавтора)
- `DELETE /api/articles/{id}/authors/{author_id}` — удалить автора
- `GET /api/articles/{id}/download` — скачать PDF (увеличить download_count)

### 2. **ArticleApprovals** endpoints
- `GET /api/approvals` — получить мои апрувы (для текущего пользователя, статус pending)
- `GET /api/articles/{id}/approvals` — получить все апрувы для статьи
- `POST /api/approvals/{id}/approve` — апрувить статью (соавтор)
- `POST /api/approvals/{id}/reject` — отклонить статью с комментарием (соавтор)

### 3. **Reviews** endpoints
- `GET /api/reviews` — получить мои рецензии (для текущего пользователя, статус pending)
- `GET /api/articles/{id}/reviews` — получить все рецензии для статьи
- `POST /api/reviews` — создать рецензию (рецензент, для статей в review)
- `PUT /api/reviews/{id}` — обновить рецензию (добавить комментарий)
- `POST /api/reviews/{id}/approve` — одобрить статью (статус approved)
- `POST /api/reviews/{id}/reject` — отклонить статью (статус rejected)
- `POST /api/reviews/{id}/request-changes` — запросить изменения

### 4. **Citations** endpoints
- `POST /api/articles/{from_id}/citations/{to_id}` — создать цитирование между статьями
- `GET /api/articles/{id}/citations` — получить все цитирования ИЗ этой статьи (на какие ссылается)
- `GET /api/articles/{id}/cited-by` — получить цитирования НА эту статью (кто ссылается)
- `DELETE /api/citations/{id}` — удалить цитирование (только автор)

### 5. **Authors** endpoints (доделать)
- `GET /api/authors` — список всех авторов (с пагинацией)
- `GET /api/authors/{id}` — профиль автора (AuthorProfile)
- `PUT /api/authors/{id}` — обновить профиль (только для себя)
- `GET /api/authors/{id}/articles` — получить статьи автора (только published)
- `GET /api/authors/{id}/statistics` — статистика (кол-во статей, цитирований, etc.)

### 6. **Reviewers** endpoints (доделать)
- `GET /api/reviewers` — список всех рецензентов
- `GET /api/reviewers/{id}` — профиль рецензента (ReviewerProfile)
- `PUT /api/reviewers/{id}` — обновить профиль (только для себя)
- `GET /api/reviewers/{id}/statistics` — статистика рецензента (кол-во рецензий, etc.)

### 7. **Journals** endpoints
- `POST /api/journals` — создать журнал (admin only)
- `GET /api/journals` — список всех журналов
- `GET /api/journals/{id}` — информация о журнале
- `PUT /api/journals/{id}` — обновить журнал (admin only)
- `DELETE /api/journals/{id}` — удалить журнал (admin only)

### 8. **Users** endpoints (проверить)
- `GET /api/users/{id}` — информация о пользователе
- `PUT /api/users/{id}` — обновить профиль (только для себя)
- `GET /api/users/me` — получить текущего пользователя (из JWT)

---

## Notes

- ✅ Journals таблица нужна для организации статей
- ✅ ArticleApprovals отдельно от Reviews (разные этапы workflow)
- ⏳ References_raw таблица — потом (для парсинга ссылок)
- 📄 Миграции Alembic уже есть, добавим в очередь
- 🔒 Нужны проверки прав доступа (только автор может редактировать draft)
- 📤 Загрузка PDF — нужно реализовать через multipart/form-data
- 🔍 Фильтрация и сортировка через query parameters (limit, offset, sort_by, order, status, year, journal_id)
- ✍️ Все endpoints кроме GET должны требовать авторизацию (JWT token)
