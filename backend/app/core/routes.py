from fastapi import FastAPI, APIRouter

def register_routes(app: FastAPI, prefix: str = "/api"):
    from app.modules.users.router import router as user_router
    from app.modules.auth.router import router as auth_router
    from app.modules.articles.router import router as article_router

    app.include_router(user_router, prefix=f"{prefix}/users", tags=["users"])
    app.include_router(auth_router, prefix=f"{prefix}/auth", tags=["auth"])
    app.include_router(article_router, prefix=f"{prefix}/articles", tags=["articles"])