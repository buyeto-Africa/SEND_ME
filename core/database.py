from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import urllib.parse

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from the environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# If DATABASE_URL contains asyncpg, replace it with psycopg2 for now
if DATABASE_URL and "asyncpg" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Declare Base class
Base = declarative_base()

# Session local for handling DB transactions
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Dependency to get the db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()