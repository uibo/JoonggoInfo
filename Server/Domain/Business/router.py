from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from Domain.DB.iPhone14_processed_info import query

router = APIRouter(
    prefix="/movingaverageline",
    tags=["movingavergeline"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def cal_mvl_data(model: str|None = None, storage: str|None = None,
                    battery: int = -1, status: int|None = None,  
                    feat_list: str = "0,0,0,0,0,0,0", db: Session=Depends(get_db)):
    records = query.select_records_by_option(db=db,model=model,storage=storage,battery=battery,status=status,feat_list=feat_list)
    return records
