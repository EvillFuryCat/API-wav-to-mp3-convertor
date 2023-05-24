from sqlalchemy import Column, String, Integer,  ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from .database_config import engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    user_name = Column(String, nullable=False)
    token = Column(postgresql.UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    
    def __init__(self, user_name=None):
        self.user_name = user_name


class Audio(Base):
    __tablename__ = "audio"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user_token = Column(postgresql.UUID(as_uuid=True), ForeignKey('user.token'), nullable=False)
    audio_token = Column(postgresql.UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    file_path = Column(String, nullable=False)

    user = relationship("User", primaryjoin="and_(Audio.user_id==User.id, Audio.user_token==User.token)", backref="audio")


Base.metadata.create_all(bind=engine)
