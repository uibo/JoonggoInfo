from sqlalchemy import Column, Integer, String, Date, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class PostInfo(Base):
    __tablename__ = "PostInfo"
    Id = Column(Integer, primary_key=True)
    Title = Column(String, nullable=True)
    Content = Column(String, nullable=True)
    Price = Column(Integer, nullable=True)
    UploadDate = Column(Date, nullable=True)
    Status  = Column(Boolean, nullable=True)
    Location = Column(String, nullable=True)
    ImgUrl = Column(String, nullable=True)
