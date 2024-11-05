from models import post
from sqlalchemy.orm import Session
from Domain.DB.post.schema import Post


def create_posts(Posts_data: list[Post] ,db: Session):
    posts = []
    for Post_data in Posts_data:
        posts.append(post(id=Post_data.id,
                          keyword=Post_data.keyword,
                          site_name=Post_data.site_name,
                          identifier=Post_data.identifier))
    db.add_all(posts)
    db.commit()

def read_posts(db: Session):
    posts = db.query(post).order_by(post.id.asc()).all()
    return posts

def read_post(id: int, db: Session):
    posts = db.query(post).filter(post.id==id).first()
    return posts

