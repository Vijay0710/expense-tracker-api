from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from templates import settings

SQLALCHEMY_DATABASE_URL = f"{settings.DATABASE_URL}:{settings.PASSWORD}@{settings.DOMAIN_NAME}:{settings.PORT}/{settings.DATABASE_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    expire_on_commit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()