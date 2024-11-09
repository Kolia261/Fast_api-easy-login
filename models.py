from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import SECRET_KEY, ALGORITHM
from datetime import datetime, timedelta
from jose import jwt

Base = declarative_base()

engine = create_engine("sqlite:///users.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    def verify_password(self, plain_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), self.password.encode('utf-8'))

    def generate_jwt(self):
        expire = datetime.utcnow() + timedelta(minutes=30)
        to_encode = {"sub": self.username, "exp": expire}
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt