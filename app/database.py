from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    JWT_SECRET_KEY: str
    JWT_REFRESH_SECRET_KEY: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

DATABASE_URL = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(
    settings.DB_USER, settings.DB_PASS, settings.DB_HOST, settings.DB_PORT, settings.DB_NAME
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
