from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
import json

from database import get_db
from Domain.DB.iPhone14_processed_info import query
import pandas as pd

router = APIRouter(
    prefix="/movingaverageline",
    tags=["movingavergeline"]
)

@router.get("/", status_code=status.HTTP_200_OK)
def cal_mvl_data(model: str|None = None, storage: str|None = None,
                    battery: int = -1, status: str = '',  
                    feat_list: str = "0000000", search_date: str = '2022-01-012024-11-30', db: Session=Depends(get_db)):
    records = query.select_records_by_option(model=model,
                                             storage=storage,
                                             battery=battery,
                                             status=status,
                                             feat_list=feat_list,
                                             search_date=search_date,
                                             db=db)
    if (bool(records)):
        data = []
        for record in records:
            data.append({"upload_date": record.upload_date,
                        "price": record.price})
        df = pd.DataFrame(data)
        df = df.groupby('upload_date').agg(price_sum=('price', 'sum'),  
                                            count=('price', 'count')).reset_index()
        df.set_index('upload_date', inplace=True)
        df.index = pd.to_datetime(df.index)
        all_dates = pd.date_range(start=df.index.min(), end=df.index.max(), freq='D')
        df = df.reindex(all_dates).fillna(0)
        mal_dict = dict()
        volume_dict = dict()
        for i in range(4, df.index.size):
            each_date = df.iloc[i].name.strftime("%Y-%m-%d")
            volume = int(df.iloc[i, 1])
            volume_dict[each_date] = volume
            days5_price_sum = int(df.iloc[i-4:i+1, 0].sum())
            days5_count_sum = int(df.iloc[i-4:i+1, 1].sum())
            mal_dict[each_date] = days5_price_sum//days5_count_sum if days5_price_sum else 0
        return [mal_dict, volume_dict]
    else:
        return None

