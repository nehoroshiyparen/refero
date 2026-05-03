from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = 'refero'
    DEBUG: bool = True

    BACKEND_HOST: str
    BACKEND_PORT: int

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int

    CLIENT_HOST: str
    CLIENT_PORT: int

    DATABASE_URL: str
    TEST_DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8"
    )

settings = Settings()