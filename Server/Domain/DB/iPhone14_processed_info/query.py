from sqlalchemy import func
from sqlalchemy.orm import Session

from models import iPhone14_processed_info

def select_records_by_option(db: Session, model: str|None = None, storage: str|None = None,
                                  battery: int = -1, status: int|None = None,  
                                  feat_list: str = "0000000"):
    query = db.query(iPhone14_processed_info)
    if model != None:
        query = query.filter(iPhone14_processed_info.model == model)
    if storage != None:
        query = query.filter(func.JSON_CONTAINS(iPhone14_processed_info.feature_list, f'"{storage}"'))
    if battery:
        query = query.filter(iPhone14_processed_info.battery >= battery)
    if status != None:
        query = query.filter(iPhone14_processed_info.status == status)
    feat_dict = {"기스": int(feat_list[0]),
                 "흠집": int(feat_list[1]),
                 "찍힘": int(feat_list[2]),
                 "파손": int(feat_list[3]),
                 "잔상": int(feat_list[4]),
                 "미개봉": int(feat_list[5]),
                 "애플케어플러스": int(feat_list[6])}
    for eachfeat in feat_dict:
        if feat_dict[eachfeat] == 1:
            query = query.filter(func.JSON_CONTAINS(iPhone14_processed_info.feature_list, f'"{eachfeat}"'))
    return query.all()

def select_record_by_id(db: Session, id: int):
    return db.query(iPhone14_processed_info).filter(iPhone14_processed_info.id == id).first()

def insert_record(db: Session, IPI):
    feature_list = [IPI.storage]
    for feat in IPI.feat_list:
        if(IPI.feat_list[feat] == 1):
            feature_list.append(feat)
    record_iPhone14pi = iPhone14_processed_info(model=IPI.model,
                                                feature_list = feature_list,
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
                                    feature_list = feature_list,
                                    battery=IPI.battery,
                                    upload_date=IPI.upload_date,
                                    price=IPI.price, 
                                    status=IPI.status,
                                    location=IPI.location,
                                    imgUrl=IPI.imgUrl,
                                    url=IPI.url)