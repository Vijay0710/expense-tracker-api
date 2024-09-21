from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_NAME = 'ExpenseTrackerDatabase'
PASSWORD = 'vijay*710'
DOMAIN_NAME = 'localhost'
DATABASE_URL = 'postgresql://postgres'

SQLALCHEMY_DATABASE_URL = f"{DATABASE_URL}:{PASSWORD}@{DOMAIN_NAME}/{DATABASE_NAME}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(
    expire_on_commit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()