from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routes import register_routes
from .deps import setup_handlers
from app.infrastructure.database.session import SessionLocal
import app.infrastructure.database.models.import_models 

class App:
    def __init__(self):
        self.fastapi_app = FastAPI(title=settings.APP_NAME)
        self.sessionmaker = SessionLocal
        self._setup()

    def get_session(self):
        async def _get_session():
            async with self.sessionmaker() as session:
                yield session
        return _get_session

    def _setup(self):
        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.fastapi_app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            import logging
            logging.exception(f"Unhandled exception on {request.method} {request.url}")
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error", "code": "INTERNAL_ERROR"},
            )

        register_routes(self.fastapi_app)
        setup_handlers(self.fastapi_app)

    def start(self):
        """Start the server"""
        import uvicorn
        uvicorn.run(
            self.fastapi_app,
            host=settings.BACKEND_HOST,
            port=settings.BACKEND_PORT,
        )

    def stop(self):
        """Stop the server"""
        pass