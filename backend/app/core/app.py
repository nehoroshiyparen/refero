from fastapi import FastAPI
from .config import settings

class App:
    def __init__(self):
        self.fastapi_app = FastAPI(title=settings.APP_NAME)
        self._setup()

    def get_session(self):
        async def _get_session():
            async with self.sessionmaker() as session:
                yield session
        return _get_session

    """
    Setups all dependencies for app
    """
    def _setup(self):
        pass

    """
    Starts up server
    """
    def start(self):
        import uvicorn
        uvicorn.run(self.fastapi_app, host=settings.BACKEND_HOST, port=settings.BACKEND_PORT)

    def stop(self):
        pass