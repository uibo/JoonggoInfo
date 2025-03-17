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

from ORM import PostInfo


class PostExtractor:
    def __init__(self, batch_size=10):
        self.batch_size = batch_size  # 한 번에 처리할 개수 설정
        
        # Selenium WebDriver 설정
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # GUI 없이 실행
        chrome_options.add_argument("--no-sandbox")  
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--log-level=3")  
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def extract(self, session):
        while True:
            # 배치 단위로 데이터 조회
            result = session.execute(
                text(f"""
                    SELECT P.Id, P.PostId 
                    FROM Post P 
                    LEFT JOIN PostInfo PI ON P.Id = PI.Id 
                    WHERE PI.Id IS NULL 
                    LIMIT {self.batch_size}
                """)
            )
            records = result.fetchall()

            if not records:  # 더 이상 처리할 데이터가 없으면 종료
                break

            extracted_data = []  # 데이터를 저장할 리스트

            for record in records:
                url = f"https://web.joongna.com/product/{record[1]}"
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
                    upload_date = complex[2].split('·')[0].strip()

                    if '전' in upload_date:
                        if '일' in upload_date:
                            now = datetime.now()
                            days_ago = int(upload_date.split('일')[0])
                            upload_date = now - timedelta(days=days_ago)
                        else:
                            upload_date = datetime.now()

                    img_url = self.driver.find_element(By.CLASS_NAME, 'col-span-1').find_element(By.TAG_NAME, 'img').get_attribute("src")

                    try:
                        status_text = self.driver.find_element(By.CLASS_NAME, 'col-span-1').find_element(By.CLASS_NAME, 'absolute').text
                        status = 1 if status_text == '판매완료' else 0
                    except:
                        status = 0

                    extracted_data.append(PostInfo(Id = record[0],Title = title,Content = content,Price = price,UploadDate= upload_date,Status = status,Location = location,ImgUrl = img_url))
                    print("Extracting Success")

                except Exception as e:
                    print(f"❌ 오류 발생 (Post ID: {record[1]})")

            if extracted_data:
                self.insert_data(session, extracted_data)

    def insert_data(self, session, data):
        session.add_all(data)
        session.commit()
        print(f"✅ {len(data)}개 삽입")


if __name__ == "__main__":
    engine = create_engine("mysql+pymysql://uibo:1231@localhost/JoonggoInfo")
    session = Session(bind=engine)

    extractor = PostExtractor(batch_size=100)  # 배치 크기 설정
    extractor.extract(session)
