from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import iPhone14_processed_info

def select_records_by_option(db: Session, model: str, storage: str,
                                  battery: int, status: str,  
                                  feature_list: str, search_date: str):
    query = db.query(iPhone14_processed_info)
    if model != None:
        query = query.filter(iPhone14_processed_info.model == model)
    if storage != None:
        query = query.filter(func.JSON_CONTAINS(iPhone14_processed_info.feature_list, f'"{storage}"'))
    if battery:
        query = query.filter(iPhone14_processed_info.battery >= battery)
    if len(status) == 1:
        query = query.filter(iPhone14_processed_info.status == int(status))
    query = query.filter(iPhone14_processed_info.upload_date>=datetime.strptime(search_date[:10],'%Y-%m-%d'))
    query = query.filter(iPhone14_processed_info.upload_date<=datetime.strptime(search_date[10:], '%Y-%m-%d'))
    feature_dict = {"기스": int(feature_list[0]),
                 "흠집": int(feature_list[1]),
                 "찍힘": int(feature_list[2]),
                 "파손": int(feature_list[3]),
                 "잔상": int(feature_list[4]),
                 "미개봉": int(feature_list[5]),
                 "애플케어플러스": int(feature_list[6])}
    for feature in feature_dict:
        if feature_dict[feature] == 1:
            query = query.filter(func.JSON_CONTAINS(iPhone14_processed_info.feature_list, f'"{feature}"'))
    return query.order_by(iPhone14_processed_info.upload_date.desc()).all()

def select_record_by_id(db: Session, id: int):
    return db.query(iPhone14_processed_info).filter(iPhone14_processed_info.id == id).first()

def insert_record(db: Session, IPI):
    record_iPhone14pi = iPhone14_processed_info(model=IPI.model,
                                                feature_list = IPI.feature_list,
                                                battery=IPI.battery,
                                                upload_date=IPI.upload_date,
                                                price=IPI.price, 
                                                status=IPI.status,
                                                location=IPI.location,
                                                imgUrl=IPI.imgUrl,
                                                url=IPI.url)
    db.add(record_iPhone14pi)
    db.commit()
    return iPhone14_processed_info(model=IPI.model,
                                    feature_list = IPI.feature_list,
                                    battery=IPI.battery,
                                    upload_date=IPI.upload_date,
                                    price=IPI.price, 
                                    status=IPI.status,
                                    location=IPI.location,
                                    imgUrl=IPI.imgUrl,
                                    url=IPI.url)