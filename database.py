from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()