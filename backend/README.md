# Refero Backend — Модели данных

Документация всех SQLAlchemy-моделей, их полей и связей.

---

## Обзор

Система использует **PostgreSQL 16** с **18 таблицами**. Каждая таблица — это SQLAlchemy-модель, наследующая `Base` (lookup-таблицы и junction-таблицы с композитным PK) или `BaseModel` (основные сущности с UUID `id`).

```
Base (DeclarativeBase)
  ├── ArticleStatusRow, ApprovalStatusRow, ReviewStatusRow  — lookup-таблицы
  ├── Role                                                  — справочник ролей
  ├── UserRole, AuthorProfile, ReviewerProfile              — junction / 1:1 профили
  │
  └── BaseModel (id: UUID = pk)
        ├── User, RefreshToken
        ├── Article, ArticleVersion, ArticleAuthors, ArticleApprovals
        ├── Journal
        ├── Citation
        ├── ReviewAssignment, Review, VersionComment
```

---

## Модуль `users` (5 таблиц)

### `User` — `users`

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `username` | `String(255)` | unique, NOT NULL |
| `email` | `String(255)` | unique, NOT NULL |
| `hashed_password` | `String(255)` | NOT NULL |
| `full_name` | `String(255)` | NOT NULL |
| `avatar_url` | `String(500)` | nullable |
| `is_active` | `Boolean` | default=True |
| `created_at` | `DateTime` | server_default=func.now() |
| `updated_at` | `DateTime` | server_default=func.now(), onupdate |

**Связи:**

| Relationship | Тип | Модель | Через поле |
|-------------|------|--------|-----------|
| `user_roles` | one-to-many | `UserRole` | FK `user_id` |
| `author_profile` | one-to-one (nullable) | `AuthorProfile` | FK `user_id` |
| `reviewer_profile` | one-to-one (nullable) | `ReviewerProfile` | FK `user_id` |
| `refresh_tokens` | one-to-many | `RefreshToken` | FK `user_id` |
| `created_articles` | one-to-many | `Article` | FK `creator_id` |
| `articles_as_author` | one-to-many | `ArticleAuthors` | FK `author_id` |
| `approvals_given` | one-to-many | `ArticleApprovals` | FK `approver_id` |
| `review_assignments` | one-to-many | `ReviewAssignment` | FK `reviewer_id` |

---

### `Role` — `roles`

Справочник ролей. **Наследует `Base`** (нет поля `id`, PK — `name`).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `name` | `Enum(RoleName)` | PK |

**Enum `RoleName`:** `GUEST`, `AUTHOR`, `REVIEWER`, `ADMIN`

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `user_roles` | one-to-many | `UserRole` |

---

### `UserRole` — `user_roles`

Junction-таблица для связи M:N между `users` и `roles`. **Наследует `Base`** (композитный PK).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `user_id` | `UUID` | PK, FK → `users.id` ON DELETE CASCADE |
| `role_name` | `String` | PK, FK → `roles.name` |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `user` | many-to-one | `User` |

---

### `AuthorProfile` — `author_profiles`

Профиль автора. **Наследует `Base`** (PK — `user_id`, 1:1 с пользователем).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `user_id` | `UUID` | PK, FK → `users.id` ON DELETE CASCADE |
| `organization` | `String(255)` | nullable |
| `position` | `String(255)` | nullable |
| `degree` | `String(100)` | nullable |
| `orcid` | `String(50)` | NOT NULL, unique |
| `bio` | `Text` | nullable |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `user` | many-to-one | `User` |

---

### `ReviewerProfile` — `reviewer_profiles`

Профиль рецензента. **Наследует `Base`** (PK — `user_id`, 1:1 с пользователем).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `user_id` | `UUID` | PK, FK → `users.id` ON DELETE CASCADE |
| `specialization` | `String(255)` | NOT NULL |
| `degree` | `String(100)` | nullable |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `user` | many-to-one | `User` |

---

## Модуль `articles` (6 таблиц)

### `Article` — `articles`

Центральная сущность — научная статья.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `current_version_id` | `UUID` | nullable, FK → `article_versions.id` |
| `creator_id` | `UUID` | NOT NULL, FK → `users.id` |
| `journal_id` | `UUID` | nullable, FK → `journals.id` |
| `doi` | `String` | unique, nullable |
| `view_count` | `Integer` | default=0 |
| `download_count` | `Integer` | default=0 |
| `is_visible` | `Boolean` | default=True, server_default=true |
| `created_at` | `DateTime` | server_default=func.now() |

**Связи:**

| Relationship | Тип | Модель | Через поле |
|-------------|------|--------|-----------|
| `creator` | many-to-one | `User` | FK `creator_id` |
| `journal` | many-to-one (nullable) | `Journal` | FK `journal_id` |
| `versions` | one-to-many | `ArticleVersion` | FK `article_id` (cascade, order by `version_number`) |
| `current_version` | one-to-one (nullable, viewonly) | `ArticleVersion` | `current_version_id` |
| `authors` | one-to-many | `ArticleAuthors` | FK `article_id` (cascade) |
| `citations_from` | one-to-many | `Citation` | FK `from_article_id` |
| `citations_to` | one-to-many | `Citation` | FK `to_article_id` |

---

### `ArticleVersion` — `article_versions`

Версия статьи (одна статья может иметь несколько версий). Каждая версия имеет собственный статус.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `article_id` | `UUID` | NOT NULL, FK → `articles.id` ON DELETE CASCADE |
| `version_number` | `Integer` | NOT NULL |
| `title` | `String` | NOT NULL |
| `abstract` | `Text` | nullable |
| `keywords` | `ARRAY(String)` | default=[] |
| `language` | `VARCHAR(5)` | default="en" |
| `pdf_path` | `String` | NOT NULL |
| `status` | `String(20)` | FK → `article_statuses.name`, default="DRAFT" |
| `updated_by_user_id` | `UUID` | nullable, FK → `users.id` |
| `published_at` | `DateTime` | nullable |
| `created_at` | `DateTime` | server_default=func.now() |
| `updated_at` | `DateTime` | server_default=func.now(), onupdate |

**Constraints:** `UniqueConstraint("article_id", "version_number")` — один номер версии на статью.

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `article` | many-to-one | `Article` |
| `updated_by_user` | many-to-one (nullable) | `User` |
| `approvals` | one-to-many | `ArticleApprovals` (cascade) |
| `review_assignment` | one-to-one (nullable) | `ReviewAssignment` (cascade) |
| `comments` | one-to-many | `VersionComment` (cascade) |

---

### `ArticleAuthors` — `article_authors`

Junction-таблица для связи M:N между статьями и пользователями (соавторы).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `article_id` | `UUID` | FK → `articles.id` ON DELETE CASCADE |
| `author_id` | `UUID` | FK → `users.id` ON DELETE CASCADE |
| `created_at` | `DateTime` | server_default=func.now() |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `article` | many-to-one | `Article` |
| `author` | many-to-one | `User` |

---

### `ArticleApprovals` — `article_approvals`

Согласование версии статьи соавтором (approval).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `article_version_id` | `UUID` | FK → `article_versions.id` ON DELETE CASCADE |
| `approver_id` | `UUID` | FK → `users.id` ON DELETE CASCADE |
| `status` | `String(20)` | FK → `approval_statuses.name`, default="PENDING" |
| `comment` | `Text` | nullable |
| `created_at` | `DateTime` | server_default=func.now() |
| `updated_at` | `DateTime` | server_default=func.now(), onupdate |
| `approved_at` | `DateTime` | nullable |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `article_version` | many-to-one | `ArticleVersion` |
| `approver` | many-to-one | `User` |

---

### `ArticleStatusRow` — `article_statuses`

Lookup-таблица статусов версий статей. **Наследует `Base`**.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `name` | `String(20)` | PK |

**Значения (из `ArticleStatus` enum):** `DRAFT`, `PENDING_APPROVAL`, `REVIEW`, `PUBLISHED`, `REJECTED`

---

### `ApprovalStatusRow` — `approval_statuses`

Lookup-таблица статусов согласования. **Наследует `Base`**.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `name` | `String(20)` | PK |

**Значения (из `ApprovalStatus` enum):** `PENDING`, `APPROVED`, `REJECTED`

---

## Модуль `journals` (1 таблица)

### `Journal` — `journals`

Научный журнал.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `name` | `String(255)` | NOT NULL, unique |
| `issn` | `String(20)` | nullable |
| `description` | `Text` | nullable |
| `created_at` | `DateTime` | server_default=func.now() |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `articles` | one-to-many | `Article` |

---

## Модуль `citations` (1 таблица)

### `Citation` — `citations`

Цитирование между статьями. Двунаправленное: `from_article_id` (цитирующая) → `to_article_id` (цитируемая). `to_article_id` может быть NULL для внешних ссылок.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `from_article_id` | `UUID` | NOT NULL, FK → `articles.id` ON DELETE CASCADE |
| `to_article_id` | `UUID` | nullable, FK → `articles.id` ON DELETE SET NULL |
| `doi` | `String(255)` | nullable |
| `raw_reference` | `Text` | nullable |
| `match_status` | `String(20)` | default="external" |
| `created_at` | `DateTime` | server_default=func.now() |

**Enum `CitationMatchStatus`:** `LINKED` (обе статьи на платформе), `PENDING` (DOI есть, статьи нет), `EXTERNAL` (внешняя ссылка)

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `from_article` | many-to-one | `Article` (цитирующая) |
| `to_article` | many-to-one (nullable) | `Article` (цитируемая) |

---

## Модуль `reviews` (4 таблицы)

### `ReviewAssignment` — `review_assignments`

Назначение рецензента на версию статьи. `article_version_id` уникален — одна версия может быть назначена только одному рецензенту в текущий момент.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `article_version_id` | `UUID` | NOT NULL, FK → `article_versions.id` ON DELETE CASCADE, **unique** |
| `reviewer_id` | `UUID` | NOT NULL, FK → `users.id` ON DELETE CASCADE |
| `created_at` | `DateTime` | server_default=func.now() |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `article_version` | many-to-one | `ArticleVersion` |
| `reviewer` | many-to-one | `User` |
| `review` | one-to-one (nullable) | `Review` (cascade) |

---

### `Review` — `reviews`

Результат рецензирования. 1:1 с назначением.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `review_assignment_id` | `UUID` | NOT NULL, FK → `review_assignments.id` ON DELETE CASCADE, **unique** |
| `status` | `String` | default="APPROVED" |
| `created_at` | `DateTime` | server_default=func.now() |
| `completed_at` | `DateTime` | nullable |

**Enum `ReviewStatus`:** `PENDING`, `APPROVED`, `REJECTED`, `REQUESTING_CHANGES`

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `assignment` | many-to-one | `ReviewAssignment` |

---

### `VersionComment` — `version_comments`

Комментарий к версии статьи (от рецензента или автора).

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `article_version_id` | `UUID` | FK → `article_versions.id` ON DELETE CASCADE |
| `user_id` | `UUID` | FK → `users.id` ON DELETE CASCADE |
| `content` | `Text` | NOT NULL |
| `created_at` | `DateTime` | server_default=func.now() |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `article_version` | many-to-one | `ArticleVersion` |
| `user` | many-to-one | `User` |

---

### `ReviewStatusRow` — `review_statuses`

Lookup-таблица статусов рецензий. **Наследует `Base`**.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `name` | `String(20)` | PK |

**Значения (из `ReviewStatus` enum):** `PENDING`, `APPROVED`, `REJECTED`, `REQUESTING_CHANGES`

---

## Модуль `auth` (1 таблица)

### `RefreshToken` — `refresh_tokens`

Refresh-токен для автоматического продления сессии.

| Поле | Тип | Ограничения |
|------|-----|-------------|
| `id` | `UUID` | PK, default=uuid4 |
| `user_id` | `UUID` | NOT NULL, FK → `users.id` ON DELETE CASCADE |
| `token_hash` | `String` | NOT NULL |
| `expires_at` | `DateTime(timezone=True)` | NOT NULL |
| `created_at` | `DateTime` | server_default=func.now() |

**Связи:**

| Relationship | Тип | Модель |
|-------------|------|--------|
| `user` | many-to-one | `User` |

---

## Полная ER-схема

```
users ──< user_roles >── roles
  │
  ├── author_profile (1:1) ──> author_profiles
  ├── reviewer_profile (1:1) ──> reviewer_profiles
  ├── refresh_tokens (1:N)
  ├── created_articles (1:N) ──> articles
  ├── articles_as_author (1:N) ──> article_authors >── articles
  ├── approvals_given (1:N) ──> article_approvals >── article_versions
  └── review_assignments (1:N) ──> review_assignments >── article_versions

journals ──< articles (1:N)

articles ──< article_versions (1:N)

article_versions ──< article_approvals (1:N)
article_versions ──< version_comments (1:N)
article_versions ──< review_assignments (1:1)
                   └── reviews (1:1)

citations: from_article_id → articles.id (цитирующая)
           to_article_id   → articles.id (цитируемая, nullable)
```

---

## Статусная модель версии

```
DRAFT ──→ PENDING_APPROVAL ──→ REVIEW ──→ PUBLISHED
  ↑                              │
  └──────────────────────────────┘
       (при REQUESTING_CHANGES)
```

- `DRAFT` — черновик, доступен автору для редактирования
- `PENDING_APPROVAL` — отправлен на согласование соавторам
- `REVIEW` — передан на рецензирование
- `PUBLISHED` — опубликован (финальный статус)
- `REJECTED` — отклонён по итогам рецензирования
- `REQUESTING_CHANGES` — рецензент запросил доработки, версия возвращается в `DRAFT`

---

## Ключевые особенности

1. **Мультиролевая модель** — пользователь может иметь несколько ролей через junction-таблицу `user_roles`. Роль `GUEST` назначается автоматически при регистрации, остальные — при создании соответствующих профилей.

2. **Версионирование статей** — `Article.current_version_id` указывает на текущую активную версию. Все исторические версии хранятся в `article_versions` с сортировкой по `version_number`.

3. **Рецензирование привязано к версии** — `ReviewAssignment.article_version_id` имеет unique-constraint: одна версия может быть назначена только одному рецензенту. При повторной отправке на рецензирование старый ассигнмент с выполненным ревью удаляется.

4. **Lookup-таблицы** — значения enum (статусы версий, статусы согласования, статусы рецензий, роли) хранятся как строки в отдельных таблицах, на которые ссылаются FK. Это обеспечивает referential integrity на уровне БД.

5. **Цитирования** — `Citation` двунаправленная: `from_article_id` (цитирующая статья) → `to_article_id` (цитируемая). `to_article_id` nullable — для внешних ссылок (DOI, raw reference).

6. **Refresh-токены** — хранятся в БД в хешированном виде. Передаются в httpOnly cookie для защиты от XSS.

7. **Счётчики просмотров** — `view_count` инкрементируется только через отдельный POST-эндпоинт (`POST /{id}/view`), а не при GET-запросе, для защиты от кэширования и ботов.

8. **`Base` vs `BaseModel`** — `Base` (без UUID id) для lookup-таблиц (PK — строковый enum) и junction-таблиц с композитным PK. `BaseModel` (с UUID id) для всех основных сущностей.

---

# API Endpoints

Всего **47 эндпоинтов** в 6 модулях. Префиксы монтируются в `app/core/routes.py`.

---

## Модуль `auth` — `/api/auth` (4 эндпоинта)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| POST | `/api/auth/register` | Регистрация | `unathorized_only` |
| POST | `/api/auth/login` | Вход | `unathorized_only` |
| POST | `/api/auth/logout` | Выход | `get_current_user` |
| POST | `/api/auth/refresh` | Обновить токен (cookie) | `get_refresh_token` |

---

## Модуль `articles` — `/api/articles` (23 эндпоинта)

### Статьи

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/articles/` | Список статей с фильтрацией | public |
| POST | `/api/articles/` | Создать статью | `AUTHOR` |
| GET | `/api/articles/{id}` | Статья по ID | public |
| PUT | `/api/articles/{id}` | Обновить статью | `AUTHOR` |
| DELETE | `/api/articles/{id}` | Удалить статью | `AUTHOR` |
| POST | `/api/articles/{id}/view` | Зарегистрировать просмотр | public |
| POST | `/api/articles/{id}/submit-for-approval` | Отправить на апрув | `AUTHOR` |
| POST | `/api/articles/{id}/hide` | Скрыть статью | `AUTHOR` |
| POST | `/api/articles/{id}/show` | Показать статью | `AUTHOR` |

### Версии

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/articles/{id}/versions` | Версии статьи | public |
| POST | `/api/articles/{id}/versions` | Создать новую версию (форк) | `AUTHOR` |
| GET | `/api/articles/{id}/versions/{version_id}` | Версия по ID | public |
| DELETE | `/api/articles/{id}/versions/{version_id}` | Удалить версию | `AUTHOR` |
| PUT | `/api/articles/{id}/versions/{version_id}/set-current` | Сделать версию текущей | `AUTHOR` |

### Согласование (approvals)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/articles/{id}/versions/{version_id}/approvals` | Апрувы версии | public |
| POST | `/api/articles/{id}/versions/{version_id}/approve` | Одобрить/отклонить | `AUTHOR` |

### PDF

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/articles/{id}/download` | Скачать PDF (текущая версия, `?inline=1`) | public |
| GET | `/api/articles/{id}/versions/{version_id}/download` | Скачать PDF версии (`?inline=1`) | public |
| POST | `/api/articles/{id}/versions/{version_id}/upload` | Загрузить PDF для версии | `AUTHOR` |

### Соавторы

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| POST | `/api/articles/{id}/authors` | Добавить соавтора | `AUTHOR` |
| DELETE | `/api/articles/{id}/authors/{author_id}` | Удалить соавтора | `AUTHOR` |

---

## Модуль `journals` — `/api/journals` (5 эндпоинтов)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/journals/` | Список журналов | public |
| GET | `/api/journals/{id}` | Информация о журнале | public |
| POST | `/api/journals/` | Создать журнал | `ADMIN` |
| PUT | `/api/journals/{id}` | Обновить журнал | `ADMIN` |
| DELETE | `/api/journals/{id}` | Удалить журнал | `ADMIN` |

---

## Модуль `users` — `/api/users` (6 эндпоинтов)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/users/` | Список пользователей | public |
| GET | `/api/users/me` | Текущий пользователь | `get_current_user` |
| GET | `/api/users/{id}` | Пользователь по ID | public |
| PUT | `/api/users/{id}` | Обновить пользователя | `get_current_user` |
| POST | `/api/users/{id}/author-profile` | Создать профиль автора | `get_current_user` |
| POST | `/api/users/{id}/reviewer-profile` | Создать профиль рецензента | `get_current_user` |

---

## Модуль `reviews` — `/api/reviews` (7 эндпоинтов)

### Назначения и рецензии

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/reviews/assignments` | Мои назначения на ревью | `REVIEWER` |
| GET | `/api/reviews/assignments/{assignment_id}` | Назначение по ID | `REVIEWER` |
| POST | `/api/reviews/assignments/{assignment_id}/review` | Вынести решение по ревью | `REVIEWER` |
| GET | `/api/reviews/assignments/{assignment_id}/review` | Получить ревью по назначению | public |

### Комментарии

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/reviews/versions/{version_id}/comments` | Комментарии к версии | public |
| POST | `/api/reviews/versions/{version_id}/comments` | Добавить комментарий | `REVIEWER`, `AUTHOR` |

### Назначение для версии (sub-router)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/articles/{id}/versions/{version_id}/assignment` | Назначение ревьюера для версии | public |

---

## Модуль `citations` — `/api/citations` (2 эндпоинта)

| Метод | URL | Описание | Авторизация |
|-------|-----|----------|-------------|
| GET | `/api/citations/{id}/citation-count` | Количество цитирований статьи | public |
| DELETE | `/api/citations/{id}` | Удалить цитирование | `AUTHOR` |

---

## Статистика по модулям

| Модуль | GET | POST | PUT | DELETE | Всего |
|--------|:---:|:----:|:---:|:------:|:-----:|
| auth | 0 | 4 | 0 | 0 | **4** |
| articles | 8 | 10 | 2 | 3 | **23** |
| journals | 2 | 1 | 1 | 1 | **5** |
| users | 3 | 2 | 1 | 0 | **6** |
| reviews | 4 | 2 | 0 | 0 | **6** |
| reviews (sub) | 1 | 0 | 0 | 0 | **1** |
| citations | 1 | 0 | 0 | 1 | **2** |
| **Итого** | **19** | **19** | **4** | **5** | **47** |
