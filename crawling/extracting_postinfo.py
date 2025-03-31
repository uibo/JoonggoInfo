import sys
import logging
import json

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session

from ORM import Post, PostInfo, UnextractedPostInfo

class PostInfoExtractor:
    def __init__(self, engine, batch_size=100):
        self.engine = engine
        self.batch_size = batch_size
        self
  
        logging.basicConfig(
            filename="./failed_post.log", 
            level=logging.ERROR, 
            format="%(asctime)s - Post ID: %(message)s")

    def extract_post_info(self):
        while True:
            extracted_postinfo = []  # 데이터를 저장할 리스트  
            unextracted_postinfo_records = []
            deleted_post = []     
            with Session(self.engine) as session:
                unextracted_postinfo_records = session.execute(select(UnextractedPostInfo).limit(self.batch_size)).scalars().all()
            if not unextracted_postinfo_records: # 더 이상 처리할 데이터가 없으면 반복문 종료
                break
        
            for post in unextracted_postinfo_records:
                url = f"https://web.joongna.com/product/{post.post_identifier}"
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                try:
                    title = soup.find('meta', {'property': "og:title"}).attrs['content']
                    content = soup.find('meta', {'property': "og:description"}).attrs['content']
                    price = json.loads(soup.find('script', {'type':"application/ld+json"}).contents[0])['offers'][0]['price']
                    uploaddate = json.loads(soup.find('script', {'id':"__NEXT_DATA__"}).contents[0])["props"]["pageProps"]["dehydratedState"]["queries"][1]["state"]["data"]["data"]["sortDate"]
                    status = 1 if soup.find('img', {'alt':"판매완료"}) else 0
                    location_tag = soup.find('path', {'id':"Subtract"})
                    location = str(location_tag.next) if location_tag else None
                    imgurl = soup.find('meta', {'property':"og:image"}).attrs['content'] 
                    extracted_postinfo.append(PostInfo(post_id = post.id, title = title, content = content, price = price, uploaddate= uploaddate, status = status, location = location, imgurl = imgurl))
                except Exception as e:
                    deleted_post.append(post)
                    logging.error(f"{post.id} - {str(e)}")

            if extracted_postinfo:
                self.insert_postinfo(extracted_postinfo)
            
            if deleted_post:
                self.update_deleted_post(deleted_post)

    def insert_postinfo(self, extracted_postinfo):
        with Session(self.engine) as session:
            session.add_all(extracted_postinfo)
            session.commit()
        print(f"✅ {len(extracted_postinfo)}개 삽입")

    def update_deleted_post(self, deleted_post):
        with Session(self.engine) as session:
            for row in deleted_post:
                session.execute(update(Post).where(Post.id==row.id).values(is_deleted=1))
            session.commit()
        print(f"❌ {len(deleted_post)}개 post 실패")
   


if __name__ == "__main__":
    engine = create_engine(f"mysql+pymysql://{sys.argv[1]}:{sys.argv[2]}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")
    extractor = PostInfoExtractor(engine) # 배치 크기 설정
    extractor.extract_post_info()
