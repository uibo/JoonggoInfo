from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status
from typing import Union

from database import get_db
from Domain.DB.post import crud
from Domain.DB.post.schema import Post

router = APIRouter(
    prefix="/post",
    tags=["post"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def posts_create(Posts_data: list[Post], db: Session=Depends(get_db)):
    crud.create_posts(Posts_data, db)

@router.get("/", status_code=status.HTTP_200_OK)
def posts_read(id: Union[int, None] = None, all: bool = False, db: Session=Depends(get_db)):
    if all == True:
        return crud.read_posts(db)
    elif type(id) == int:
        return crud.read_post(id, db)
    else:
        return "Require path: id or all"
    


