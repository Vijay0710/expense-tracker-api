from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import settings

SQLALCHEMY_DATABASE_URL = f"{settings.DATABASE_URL}:{settings.PASSWORD}@{settings.DOMAIN_NAME}/{settings.DATABASE_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(
    expire_on_commit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()