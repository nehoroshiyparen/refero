"""
Seed: основные таблицы по 5–6 записей, остальные по 2–3.

Распределение:
  roles                  4  GUEST, AUTHOR, REVIEWER, ADMIN
  article_statuses       5  DRAFT, PENDING_APPROVAL, REVIEW, PUBLISHED, REJECTED
  approval_statuses      3  PENDING, APPROVED, REJECTED
  review_statuses        4  PENDING, APPROVED, REJECTED, REQUESTING_CHANGES
  ─────────────────────────────────────────────────────────
  users                  6  ★ основная
  user_roles             7  (6 users, sidorov имеет 2 роли)
  author_profiles        3
  reviewer_profiles      2
  journals               3  ★
  articles               5  ★
  article_versions       6  ★ (1 статья с 2 версиями)
  article_authors        7  (5 связей создатель + 2 соавтора)
  article_approvals      2
  citations              2
  review_assignments     2
  reviews                2
  version_comments       2
  refresh_tokens         0  —

Usage: docker compose exec backend python seed_40.py
"""
import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import settings
from app.modules.auth.utils.hash_password import hash_password

import app.infrastructure.database.models.import_models

from app.modules.users.models.user import User
from app.modules.users.models.user_role import UserRole
from app.modules.users.models.author_profile import AuthorProfile
from app.modules.users.models.reviewer_profile import ReviewerProfile
from app.modules.journals.models.journal import Journal
from app.modules.articles.models.article import Article
from app.modules.articles.models.article_version import ArticleVersion
from app.modules.articles.models.article_authors import ArticleAuthors
from app.modules.articles.models.article_approvals import ArticleApprovals
from app.modules.reviews.models.review_assignment import ReviewAssignment
from app.modules.reviews.models.review import Review
from app.modules.reviews.models.version_comment import VersionComment
from app.modules.citations.models.citation import Citation


def now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as session:

        # ── lookup tables (4+5+3+4 = 16) ─────────────────────────
        lookups = {
            "roles": ["GUEST", "AUTHOR", "REVIEWER", "ADMIN"],
            "article_statuses": ["DRAFT", "PENDING_APPROVAL", "REVIEW", "PUBLISHED", "REJECTED"],
            "approval_statuses": ["PENDING", "APPROVED", "REJECTED"],
            "review_statuses": ["PENDING", "APPROVED", "REJECTED", "REQUESTING_CHANGES"],
        }
        for table, vals in lookups.items():
            for v in vals:
                await session.execute(
                    text(f"INSERT INTO {table} (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                    {"name": v},
                )
        await session.commit()

        # ── users × 6 ────────────────────────────────────────────
        admin = User(username="admin", email="admin@refero.org",
                     hashed_password=hash_password("admin123"),
                     full_name="Администратор")
        ivanov = User(username="ivanov", email="ivanov@refero.org",
                      hashed_password=hash_password("author123"),
                      full_name="Иван Иванов")
        petrova = User(username="petrova", email="petrova@refero.org",
                       hashed_password=hash_password("author123"),
                       full_name="Мария Петрова")
        sidorov = User(username="sidorov", email="sidorov@refero.org",
                       hashed_password=hash_password("author123"),
                       full_name="Сергей Сидоров")
        kuznetsova = User(username="kuznetsova", email="kuznetsova@refero.org",
                          hashed_password=hash_password("reviewer123"),
                          full_name="Анна Кузнецова")
        smirnov = User(username="smirnov", email="smirnov@refero.org",
                       hashed_password=hash_password("author123"),
                       full_name="Дмитрий Смирнов")
        session.add_all([admin, ivanov, petrova, sidorov, kuznetsova, smirnov])
        await session.flush()

        # ── user_roles × 7 ───────────────────────────────────────
        session.add_all([
            UserRole(user_id=admin.id, role_name="ADMIN"),
            UserRole(user_id=ivanov.id, role_name="AUTHOR"),
            UserRole(user_id=petrova.id, role_name="AUTHOR"),
            UserRole(user_id=sidorov.id, role_name="AUTHOR"),
            UserRole(user_id=sidorov.id, role_name="REVIEWER"),
            UserRole(user_id=kuznetsova.id, role_name="REVIEWER"),
            UserRole(user_id=smirnov.id, role_name="AUTHOR"),
        ])
        await session.flush()

        # ── profiles: 3 author + 2 reviewer ──────────────────────
        session.add_all([
            AuthorProfile(user_id=ivanov.id, orcid="0000-0001-1111-1111",
                          organization="МГУ", position="Ст. науч. сотрудник",
                          degree="PhD", bio="Компьютерные науки"),
            AuthorProfile(user_id=petrova.id, orcid="0000-0002-2222-2222",
                          organization="СПбГУ", position="Доцент",
                          degree="PhD", bio="Биомедицина"),
            AuthorProfile(user_id=sidorov.id, orcid="0000-0003-3333-3333",
                          organization="НГУ", position="Профессор",
                          degree="DSc", bio="Машинное обучение"),
            ReviewerProfile(user_id=sidorov.id, specialization="Computer Science",
                            degree="DSc"),
            ReviewerProfile(user_id=kuznetsova.id, specialization="Biomedicine",
                            degree="PhD"),
        ])
        await session.flush()

        # ── journals × 3 ─────────────────────────────────────────
        j_cs = Journal(name="Journal of Computer Science", issn="1111-1111",
                       description="Computer science research")
        j_bio = Journal(name="Biomedical Research", issn="2222-2222",
                        description="Biomedical research")
        j_phys = Journal(name="Physics Letters", issn="3333-3333",
                         description="Physics research")
        session.add_all([j_cs, j_bio, j_phys])
        await session.flush()

        # ── helper: create article + version + authorship ────────
        async def make_article(creator, journal, title, abstract, keywords, lang, status,
                               version_number=1, days_ago=0):
            article = Article(creator_id=creator.id, journal_id=journal.id)
            session.add(article)
            await session.flush()

            published = now() - timedelta(days=days_ago) if status == "PUBLISHED" else None
            version = ArticleVersion(
                article_id=article.id, version_number=version_number,
                title=title, abstract=abstract, keywords=keywords,
                language=lang, pdf_path="seeds/sample.pdf",
                status=status, updated_by_user_id=creator.id,
                published_at=published,
            )
            session.add(version)
            await session.flush()

            article.current_version_id = version.id

            authorship = ArticleAuthors(article_id=article.id, author_id=creator.id)
            session.add(authorship)
            await session.flush()

            return article, version

        # ── articles × 5 / versions × 6 ──────────────────────────
        art1, ver1 = await make_article(
            ivanov, j_cs,
            "Deep Learning in NLP",
            "Обзор методов глубокого обучения в задачах NLP.",
            ["deep learning", "NLP", "transformers"], "ru", "PUBLISHED", days_ago=30,
        )
        art2, ver2 = await make_article(
            petrova, j_bio,
            "CRISPR-Cas9: Advances in Gene Editing",
            "Обзор достижений в технологии CRISPR-Cas9.",
            ["CRISPR", "gene editing", "Cas9"], "en", "PUBLISHED", days_ago=20,
        )
        art3, ver3 = await make_article(
            ivanov, j_cs,
            "Neural Networks for Image Recognition",
            "Сравнение архитектур CNN для классификации изображений.",
            ["CNN", "image recognition"], "en", "DRAFT",
        )
        art4, ver4_v1 = await make_article(
            sidorov, j_cs,
            "Reinforcement Learning in Robotics",
            "Применение RL в робототехнике. Первая версия.",
            ["reinforcement learning", "robotics"], "en", "DRAFT", version_number=1,
        )
        # art4: вторая версия, отправлена на ревью
        ver4_v2 = ArticleVersion(
            article_id=art4.id, version_number=2,
            title="Reinforcement Learning in Robotics (revised)",
            abstract="Применение RL в робототехнике. Исправленная версия.",
            keywords=["reinforcement learning", "robotics", "policy gradients"],
            language="en", pdf_path="seeds/sample.pdf",
            status="REVIEW", updated_by_user_id=sidorov.id,
        )
        session.add(ver4_v2)
        await session.flush()
        art4.current_version_id = ver4_v2.id

        art5, ver5 = await make_article(
            smirnov, j_phys,
            "Quantum Entanglement in Many-Body Systems",
            "Анализ квантовой запутанности в многочастичных системах.",
            ["quantum entanglement", "many-body"], "en", "PUBLISHED", days_ago=10,
        )

        # ── article_authors: +2 соавтора (всего 7) ───────────────
        session.add(ArticleAuthors(article_id=art4.id, author_id=petrova.id))
        session.add(ArticleAuthors(article_id=art5.id, author_id=ivanov.id))
        await session.flush()

        # ── article_approvals × 2 ────────────────────────────────
        session.add(ArticleApprovals(
            article_version_id=ver4_v2.id, approver_id=petrova.id,
            status="APPROVED", approved_at=now(),
        ))
        session.add(ArticleApprovals(
            article_version_id=ver4_v2.id, approver_id=sidorov.id,
            status="APPROVED", approved_at=now(),
        ))
        await session.flush()

        # ── citations × 2 ────────────────────────────────────────
        session.add(Citation(
            from_article_id=art1.id, to_article_id=art2.id,
            match_status="linked",
            raw_reference="Petrova M. CRISPR-Cas9 Advances. Biomed Res. 2026.",
        ))
        session.add(Citation(
            from_article_id=art5.id, to_article_id=art4.id,
            match_status="linked",
            raw_reference="Sidorov S. RL in Robotics. J Comput Sci. 2026.",
        ))
        await session.flush()

        # ── review_assignments × 2 + reviews × 2 ─────────────────
        # art1 (PUBLISHED) — completed review
        ra1 = ReviewAssignment(article_version_id=ver1.id, reviewer_id=kuznetsova.id)
        session.add(ra1)
        await session.flush()
        session.add(Review(
            review_assignment_id=ra1.id, status="APPROVED",
            completed_at=now() - timedelta(days=15),
        ))

        # art4 v2 (REVIEW) — pending review
        ra2 = ReviewAssignment(article_version_id=ver4_v2.id, reviewer_id=kuznetsova.id)
        session.add(ra2)
        await session.flush()

        # ── version_comments × 2 ─────────────────────────────────
        session.add(VersionComment(
            article_version_id=ver1.id, user_id=kuznetsova.id,
            content="Хорошая работа, рекомендую к публикации.",
        ))
        session.add(VersionComment(
            article_version_id=ver4_v2.id, user_id=kuznetsova.id,
            content="Необходимо добавить раздел с анализом сходимости алгоритмов.",
        ))
        await session.flush()

        # ── финал ────────────────────────────────────────────────
        await session.commit()

        print(
            "Seed completed.\n"
            "  admin      / admin123     (ADMIN)\n"
            "  ivanov     / author123    (AUTHOR)\n"
            "  petrova    / author123    (AUTHOR)\n"
            "  sidorov    / author123    (AUTHOR + REVIEWER)\n"
            "  kuznetsova / reviewer123  (REVIEWER)\n"
            "  smirnov    / author123    (AUTHOR)"
        )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
