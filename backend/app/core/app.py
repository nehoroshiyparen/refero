from fastapi import FastAPI
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
        """Setup all dependencies for app"""
        register_routes(self.fastapi_app)
        setup_handlers(self.fastapi_app)

        self.fastapi_app.add_middleware(
            CORSMiddleware,
            allow_origins=[f"http://{settings.CLIENT_HOST}:{settings.CLIENT_PORT}"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

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