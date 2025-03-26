import sys
import logging
from datetime import datetime, timedelta
import json

import requests
from bs4 import BeautifulSoup

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ORM import PostInfo, UnextractedPostInfo


class PostInfoExtractor:
    def __init__(self, batch_size=100):
        self.batch_size = batch_size
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # GUI 없이 실행
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")  
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

        logging.basicConfig(
            filename="./failed_post.log", 
            level=logging.ERROR, 
            format="%(asctime)s - Post ID: %(message)s"
        )

    def extract_post_info(self, session):
        while True:
            extracted_postinfo = []  # 데이터를 저장할 리스트        
            unextracted_postinfo_records = session.query(UnextractedPostInfo).limit(self.batch_size).all()
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
                    logging.error(f"{post.id} - {str(e)}")  

            if extracted_postinfo:
                self.insert_postinfo(session, extracted_postinfo)       

    def insert_postinfo(self, session, data):
        session.add_all(data)
        session.commit()
        print(f"✅ {len(data)}개 삽입")


if __name__ == "__main__":
    engine = create_engine(f"mysql+pymysql://{sys.argv[1]}:{sys.argv[2]}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")
    session = Session(bind=engine)
    extractor = PostInfoExtractor() # 배치 크기 설정
    extractor.extract_post_info(session)
