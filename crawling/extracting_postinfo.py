import sys
import logging
from datetime import datetime, timedelta

import pandas as pd
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
                self.driver.get(url)
                try:
                    WebDriverWait(self.driver, 2).until(EC.presence_of_element_located((By.TAG_NAME, "article")))
                    content = self.driver.find_element(By.TAG_NAME, 'article').text
                    if "거래희망지역" in content:
                        content, location = content.split("거래희망지역")
                    else:
                        location = None
                    # 제목, 가격, 업로드 날짜 추출
                    title_tag = self.driver.find_element(By.TAG_NAME, 'h1')
                    complex = self.driver.execute_script("return arguments[0].parentNode;", title_tag)
                    complex = self.driver.execute_script("return arguments[0].parentNode;", complex)
                    complex = complex.text.split('\n')
                    title = complex[0]
                    price = int(complex[1].replace("원", "").replace(",", ""))
                    uploaddate = complex[2].split('·')[0].strip()
                    if '전' in uploaddate:
                        if '일' in uploaddate:
                            now = datetime.now()
                            days_ago = int(uploaddate.split('일')[0])
                            uploaddate = now - timedelta(days=days_ago)
                        else:
                            uploaddate = datetime.now()
                    img_url = self.driver.find_element(By.CLASS_NAME, 'col-span-1').find_element(By.TAG_NAME, 'img').get_attribute("src")
                    status = 1 if "판매완료" in self.driver.find_element(By.CLASS_NAME, 'col-span-1').text else 0
                    extracted_postinfo.append(PostInfo(post_id = post.id, title = title, content = content, price = price, uploaddate= uploaddate, status = status, location = location, imgurl = img_url))
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
