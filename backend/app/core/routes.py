from fastapi import FastAPI, APIRouter

def register_routes(app: FastAPI, prefix: str = "/api"):
    from app.modules.users.router import router as user_router
    from app.modules.auth.router import router as auth_router
    from app.modules.articles.router import router as article_router
    from app.modules.citations.router import router as citation_router
    from app.modules.journals.router import router as journal_router
    from app.modules.reviews.router import router as review_router, article_reviews_router

    app.include_router(user_router, prefix=f"{prefix}/users", tags=["users"])
    app.include_router(auth_router, prefix=f"{prefix}/auth", tags=["auth"])
    app.include_router(article_router, prefix=f"{prefix}/articles", tags=["articles"])
    app.include_router(citation_router, prefix=f"{prefix}/citations", tags=["citations"])
    app.include_router(journal_router, prefix=f"{prefix}/journals", tags=["journals"])
    app.include_router(review_router, prefix=f"{prefix}/reviews", tags=["reviews"])
    app.include_router(article_reviews_router, tags=["reviews", "articles"])