from sqlalchemy import Column, Integer, String, Date, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(String(255), nullable=False)
    site = Column(String(255), nullable=False)
    post_identifier = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, nullable=False ,default=0)

class PostInfo(Base):
    __tablename__ = "postinfo"
    post_id = Column(Integer, primary_key=True)
    title = Column(String(65535), nullable=True)
    content = Column(String(65535), nullable=True)
    price = Column(Integer, nullable=True)
    uploaddate = Column(Date, nullable=True)
    status  = Column(Boolean, nullable=True)
    location = Column(String(255), nullable=True)
    url = Column(String(255), nullable=True)
    imgurl = Column(String(255), nullable=True)
    conditions = Column(JSON, nullable=True, default=list)

class Pending_Post(Base):
    __tablename__ = 'pending_post'
    id = Column(Integer, primary_key=True)
    site = Column(String(255), nullable=False)
    post_identifier = Column(Integer, nullable=False)