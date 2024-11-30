from sqlalchemy import Column, Integer, String, Date, Boolean, JSON
from database import Base

class iPhone14_processed_info(Base):
    __tablename__ = "iphone14_processed_info"
    id = Column(Integer, autoincrement=True, primary_key=True) # Auto_increment로 순차적 부여, Primary key
    model = Column(String, nullable=False)
    feature_list = Column(JSON, nullable=False)
    battery = Column(Integer, nullable=False)
    upload_date = Column(Date, nullable=False)
    price = Column(Integer, nullable=False)
    status = Column(Boolean, nullable=False)
    location = Column(String, nullable=True)
    imgUrl = Column(String, nullable=False)
    url = Column(String, nullable=False)


