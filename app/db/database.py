from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.settings import settings
from sqlalchemy.ext.declarative import declarative_base

# Database URL, set in .env file
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# Database engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Create all tables
Base.metadata.create_all(bind=engine)
