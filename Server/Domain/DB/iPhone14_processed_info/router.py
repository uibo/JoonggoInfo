from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from Domain.DB.iPhone14_processed_info import query

class IPhone14ProcessedInfo(BaseModel):
    model: str
    storage: str
    battery: int = -1
    upload_date: str
    price: int
    status: int
    location: str 
    imgUrl: str
    url: str
    feat_list: dict

router = APIRouter(
    prefix="/iPhone14_processed_info",
    tags=["iPhone14_processed_info"]
)
@router.get("/", status_code=status.HTTP_200_OK)
def read_records_by_option(model: str|None = None, storage: str|None = None,
                                  battery: int = -1, status: int|None = None,  
                                  feat_list: str = "0000000", search_date: str = '2022-01-012024-11-30', db: Session=Depends(get_db)):
    return query.select_records_by_option(model=model,
                                          storage=storage,
                                          battery=battery,
                                          status=status,
                                          feat_list=feat_list,
                                          search_date=search_date,
                                          db=db)
    
@router.get("/{id}", status_code=status.HTTP_200_OK)
def read_record_by_id(id: int, db: Session=Depends(get_db)):
    return query.select_record_by_id(id=id, db=db)

@router.post("/", status_code=status.HTTP_201_CREATED)
def insert_record(IPI: IPhone14ProcessedInfo, db: Session=Depends(get_db)):
    return query.insert_record(db=db, IPI=IPI)