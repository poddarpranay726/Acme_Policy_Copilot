import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")


# Creates connection pool for PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
)


# Creates individual database sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


# Base class for database models
class Base(DeclarativeBase):
    pass


# FastAPI database dependency
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# Test database connection
if __name__ == "__main__":
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("Connected successfully!")
        print(result.scalar())
