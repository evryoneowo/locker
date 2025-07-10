import os

from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, Integer, BigInteger, Text, LargeBinary, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    salt = Column(LargeBinary, nullable=False)

    passwords = relationship('Password', back_populates='user')


class Password(Base):
    __tablename__ = 'passwords'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    service = Column(Text, nullable=False)
    login = Column(Text, nullable=False)
    password_enc = Column(LargeBinary, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    nonce = Column(LargeBinary, nullable=False)

    user = relationship('User', back_populates='passwords')

load_dotenv()
engine = create_engine(os.getenv('DATABASE_URL'))

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
