from sqlalchemy import Column, Integer, String, Date, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True, autoincrement=True)
    product = Column(String, nullable=True)
    site = Column(String, nullable=False)
    post_identifier = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=0)
    
class PostInfo(Base):
    __tablename__ = "postinfo"
    post_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    uploaddate = Column(Date, nullable=True)
    status  = Column(Boolean, nullable=True)
    location = Column(String, nullable=True)
    imgurl = Column(String, nullable=True)

class BunjangPostInfoTest(Base):
    __tablename__ = "bunjang_postinfo_test"
    post_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=True)
    content = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    uploaddate = Column(Date, nullable=True)
    status  = Column(Boolean, nullable=False)
    location = Column(String, nullable=True)
    imgurl = Column(String, nullable=True)
    conditions = Column(JSON, nullable=True)

class UnextractedPostInfo(Base):
    __tablename__ = "unextracted_postinfo"
    id = Column(Integer, primary_key=True, autoincrement=True)
    site = Column(String, nullable=False)
    post_identifier = Column(Integer, nullable=False)

