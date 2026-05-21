"""
Seed script: creates mock users, journals, articles, and reviews.

Usage: docker compose exec backend python seed.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta, timezone

def now_utc():
    return datetime.now(timezone.utc).replace(tzinfo=None)

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
from app.modules.reviews.models.review_assignment import ReviewAssignment
from app.modules.reviews.models.review import Review


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async with AsyncSession(engine) as session:
        # ── справочники ──────────────────────────────────────────
        for table, vals in [
            ("article_statuses", ["DRAFT", "PENDING_APPROVAL", "REVIEW", "PUBLISHED", "REJECTED"]),
            ("approval_statuses", ["PENDING", "APPROVED", "REJECTED"]),
            ("review_statuses", ["PENDING", "APPROVED", "REJECTED", "REQUESTING_CHANGES"]),
        ]:
            for v in vals:
                await session.execute(
                    text(f"INSERT INTO {table} (name) VALUES (:name) ON CONFLICT (name) DO NOTHING"),
                    {"name": v},
                )
        await session.commit()

        # ── пользователи ─────────────────────────────────────────
        admin = User(
            username="admin", email="admin@refero.org",
            hashed_password=hash_password("admin123"),
            full_name="Администратор",
        )
        author1 = User(
            username="ivanov", email="ivanov@refero.org",
            hashed_password=hash_password("author123"),
            full_name="Иван Иванов",
        )
        author2 = User(
            username="petrova", email="petrova@refero.org",
            hashed_password=hash_password("author123"),
            full_name="Мария Петрова",
        )
        reviewer1 = User(
            username="sidorov", email="sidorov@refero.org",
            hashed_password=hash_password("reviewer123"),
            full_name="Пётр Сидоров",
        )
        session.add_all([admin, author1, author2, reviewer1])
        await session.flush()

        session.add_all([
            UserRole(user_id=admin.id, role_name="ADMIN"),
            UserRole(user_id=author1.id, role_name="AUTHOR"),
            UserRole(user_id=author2.id, role_name="AUTHOR"),
            UserRole(user_id=reviewer1.id, role_name="REVIEWER"),
        ])
        await session.flush()

        # Проверяем, есть ли уже профили (seed идемпотентен)
        existing_author = await session.get(AuthorProfile, author1.id)
        if not existing_author:
            session.add_all([
                AuthorProfile(user_id=author1.id, orcid="0000-0001-2345-6789",
                              organization="МГУ им. Ломоносова", position="Старший научный сотрудник",
                              degree="PhD", bio="Исследователь в области компьютерных наук"),
                AuthorProfile(user_id=author2.id, orcid="0000-0002-9876-5432",
                              organization="СПбГУ", position="Доцент",
                              degree="PhD", bio="Биомедицинский исследователь"),
                ReviewerProfile(user_id=reviewer1.id, specialization="Computer Science",
                                degree="PhD"),
            ])
            await session.flush()

        # ── журналы ──────────────────────────────────────────────
        j_cs = Journal(name="Journal of Computer Science", issn="1234-5678",
                       description="Современные исследования в области компьютерных наук")
        j_bio = Journal(name="Biomedical Research Review", issn="2345-6789",
                        description="Рецензируемый журнал по биомедицинским исследованиям")
        j_quant = Journal(name="Quantum Physics Letters", issn="3456-7890",
                          description="Международный журнал по квантовой физике")
        session.add_all([j_cs, j_bio, j_quant])
        await session.flush()

        # ── статьи ───────────────────────────────────────────────
        async def make_article(creator, journal, title, abstract, keywords, lang, status,
                               version_number=1, days_ago=0):
            article = Article(creator_id=creator.id, journal_id=journal.id if journal else None)
            session.add(article)
            await session.flush()

            published = now_utc() - timedelta(days=days_ago) if status == "PUBLISHED" else None
            version = ArticleVersion(
                article_id=article.id,
                version_number=version_number,
                title=title,
                abstract=abstract,
                keywords=keywords,
                language=lang,
                pdf_path="seeds/sample.pdf",
                status=status,
                updated_by_user_id=creator.id,
                published_at=published,
            )
            session.add(version)
            await session.flush()

            article.current_version_id = version.id

            authorship = ArticleAuthors(article_id=article.id, author_id=creator.id)
            session.add(authorship)
            await session.flush()

            return article, version

        art1, ver1 = await make_article(
            author1, j_cs,
            "Deep Learning Approaches in Natural Language Processing",
            "Обзор современных методов глубокого обучения в задачах обработки естественного языка. "
            "Рассматриваются трансформеры, attention-механизмы и предобученные языковые модели.",
            ["deep learning", "NLP", "transformers"], "ru", "PUBLISHED", days_ago=30,
        )
        art2, ver2 = await make_article(
            author1, j_cs,
            "A Survey of Reinforcement Learning Techniques",
            "Комплексный обзор методов обучения с подкреплением, включая Q-learning, "
            "policy gradients и глубокие RL-алгоритмы.",
            ["reinforcement learning", "Q-learning", "deep RL"], "en", "PUBLISHED", days_ago=14,
        )
        art3, ver3 = await make_article(
            author1, j_cs,
            "Neural Networks for Image Recognition: A Comparative Study",
            "Сравнительный анализ архитектур свёрточных нейронных сетей для задач "
            "классификации изображений на наборе данных ImageNet.",
            ["CNN", "image recognition", "ImageNet"], "en", "DRAFT",
        )
        art4, ver4 = await make_article(
            author2, j_bio,
            "CRISPR-Cas9: Advances in Gene Editing",
            "Обзор последних достижений в технологии CRISPR-Cas9 для редактирования генома. "
            "Обсуждаются новые варианты Cas-белков и методы доставки.",
            ["CRISPR", "gene editing", "Cas9"], "en", "PUBLISHED", days_ago=21,
        )
        art5, ver5 = await make_article(
            author2, j_bio,
            "The Role of Microbiome in Human Health",
            "Исследование влияния микробиома кишечника на иммунную систему, метаболизм "
            "и развитие хронических заболеваний.",
            ["microbiome", "gut health", "immunology", "metabolism"], "en", "REVIEW",
        )
        art6, ver6 = await make_article(
            author1, j_quant,
            "Квантовая запутанность в многочастичных системах",
            "Теоретический анализ квантовой запутанности в системах с многими "
            "частицами и её роль в квантовых вычислениях.",
            ["квантовая запутанность", "квантовые вычисления", "многочастичные системы"],
            "ru", "PUBLISHED", days_ago=7,
        )

        # ── ревью ─────────────────────────────────────────────────
        assignment1 = ReviewAssignment(
            article_version_id=ver4.id, reviewer_id=reviewer1.id,
        )
        session.add(assignment1)
        await session.flush()

        session.add(Review(
            review_assignment_id=assignment1.id,
            status="APPROVED",
            completed_at=now_utc() - timedelta(days=10),
        ))

        session.add(ReviewAssignment(
            article_version_id=ver5.id, reviewer_id=reviewer1.id,
        ))

        assignment3 = ReviewAssignment(
            article_version_id=ver2.id, reviewer_id=reviewer1.id,
        )
        session.add(assignment3)
        await session.flush()

        session.add(Review(
            review_assignment_id=assignment3.id,
            status="APPROVED",
            completed_at=now_utc() - timedelta(days=7),
        ))

        await session.commit()
        print(
            "Seed completed.\n"
            "  admin / admin123  (ADMIN)\n"
            "  ivanov / author123  (AUTHOR)\n"
            "  petrova / author123  (AUTHOR)\n"
            "  sidorov / reviewer123  (REVIEWER)"
        )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
