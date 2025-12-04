from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

DATABASE_URL = get_settings().database_url

# Создаем engine с timeout настройками
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_timeout=10,             # Timeout для получения connection из pool
    pool_recycle=100,            # Переподключение каждый час
    connect_args={
        "connect_timeout": 10,   # Timeout подключения к PostgreSQL
        "application_name": "chat-api"
    } if DATABASE_URL.startswith("postgresql") else {}
)


def init_db() -> None:
    """Инициализация базы данных - создание таблиц"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency для получения сессии БД"""
    with Session(engine) as session:
        yield session
