from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from gymhero.config import settings

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)  # echo only for debug
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
