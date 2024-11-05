from pydantic import BaseModel

class Post(BaseModel):
    id: None
    keyword: str
    site_name: str
    identifier: int

