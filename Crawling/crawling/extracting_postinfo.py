import sys

import traceback
import json
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from ORM import Post, PostInfo, Post_To_Extract_Info

class PostInfoExtractor:
    def __init__(self, engine, batch_size=100):
        self.engine = engine
        self.batch_size = batch_size

class JoongnaPostInfoExtractor(PostInfoExtractor):
    def __init__(self, engine):
        super().__init__(engine)

    def extract_postinfo(self):
        while True:
            extracted_postinfo = []  # 데이터를 저장할 리스트  
            deleted_rows = []     
            with Session(self.engine) as session:
                post_to_extract_info_rows = session.execute(select(Post_To_Extract_Info).where(Post_To_Extract_Info.site =='joongnaweb').limit(self.batch_size)).scalars().all()
            if not post_to_extract_info_rows: # 더 이상 처리할 데이터가 없으면 반복문 종료
                break
        
            for row in post_to_extract_info_rows:
                url = f"https://web.joongna.com/product/{row.post_identifier}"
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
                    extracted_postinfo.append(PostInfo(post_id = row.id, title = title, content = content, price = price, uploaddate = uploaddate, status = status, location = location, imgurl = imgurl))
                except Exception as e:
                    print(traceback.format_exc())
                    deleted_rows.append(row)

            if extracted_postinfo:
                self.insert_postinfo(extracted_postinfo)
            
            if deleted_rows:
                self.update_deleted_row(deleted_rows)

    def insert_postinfo(self, extracted_postinfo):
        with Session(self.engine) as session:
            session.add_all(extracted_postinfo)
            session.commit()
        print(f"✅postinfo {len(extracted_postinfo)}개 삽입")

    def update_deleted_row(self, deleted_rows):
        with Session(self.engine) as session:
            for row in deleted_rows:
                session.execute(update(Post).where(Post.id==row.id).values(is_deleted=1))
            session.commit()
        print(f"❌postinfo {len(deleted_rows)}개 실패")
   
class BunjangPostInfoExtractor(PostInfoExtractor):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUI 없이 실행
    chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
    chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화
    chrome_options.add_argument("--log-level=3")
    xpath_dict = {'title': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div[1]',
              'content': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[1]/p',
              'price': '/html/body/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div',
              'uploaddate': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div/div[3]',
              'location': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div/span',
              'condition': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]',
              'imgurl': '/html/body/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div[1]/div/div[1]/div/img[1]',
              'soldout_status': "/html/body/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div[1]/div/div[1]/div[2]/div/img"}

    def __init__(self, engine):
        super().__init__(engine)
        self.driver = webdriver.Chrome(options=self.chrome_options)
        self.driver.implicitly_wait(5)
    
    def extract_postinfo(self):
        while True:
            with Session(self.engine) as session:
                post_to_extract_info_rows = session.execute(select(Post_To_Extract_Info).where(Post_To_Extract_Info.site =='bunjang').limit(self.batch_size)).scalars().all()
            if not post_to_extract_info_rows: # 더 이상 처리할 데이터가 없으면 반복문 종료
                break
            
            deleted_rows = set()
            rows = set()
            for row in post_to_extract_info_rows:
                url = f"https://m.bunjang.co.kr/products/{row.post_identifier}?original=1"
                self.driver.get(url)
                try:
                    title = self.driver.find_elements(By.XPATH, self.xpath_dict['title'])[0].text
                    content = self.driver.find_elements(By.XPATH, self.xpath_dict['content'])[0].text
                    imgurl = self.driver.find_element(By.XPATH, self.xpath_dict['imgurl']).get_attribute('src')
                    price = int((self.driver.find_elements(By.XPATH, self.xpath_dict['price'])[0].text)[:-1].replace(',', ''))
                    status = self.driver.find_elements(By.XPATH, self.xpath_dict['soldout_status'])
                    status = 1 if status else 0
                    address = self.driver.find_elements(By.XPATH, self.xpath_dict['location'])
                    if address:
                        match = re.search(r'\s(\S+동)', address[0].text)
                        location = match.group(1) if match else None
                    uploaddate = self.driver.find_elements(By.XPATH, self.xpath_dict['uploaddate'])[0].text
                    uploaddate = self.parse_relative_time(uploaddate)
                    condition = self.driver.find_elements(By.XPATH, self.xpath_dict['condition'])
                    if condition:
                        conditions = [condition[0].text]
                    rows.add(PostInfo(post_id=row.id, title=title, content=content, price=price, uploaddate=uploaddate, status=status, location=location, imgurl=imgurl, conditions=conditions))
                except Exception as e:
                    print("failed: ", url)
                    deleted_rows.add(row)

            if rows:
                with Session(self.engine) as session:
                    session.add_all(rows)
                    session.commit()
                print(f"✅postinfo {len(rows)}개 삽입")
            
            if deleted_rows:
                self.update_deleted_row(deleted_rows)


    def update_deleted_row(self, deleted_rows):
            with Session(self.engine) as session:
                for post in deleted_rows:
                    session.execute(update(Post).where(Post.id==post.id).values(is_deleted=1))
                session.commit()
            print(f"❌postinfo {len(deleted_rows)}개 실패")

    def parse_relative_time(self, text, base_time=None):
        if base_time is None:
            base_time = datetime.now()

        # 매칭
        match = re.match(r'(\d+)\s*(분|시간|일|주|달|년) 전', text)
        if not match:
            return None

        value, unit = int(match.group(1)), match.group(2)

        if unit == '분':
            post_time = base_time - timedelta(minutes=value)
            return post_time.strftime('%Y-%m-%d')  # 정확한 시간까지 반환

        elif unit == '시간':
            post_time = base_time - timedelta(hours=value)
            return post_time.strftime('%Y-%m-%d')

        elif unit == '일':
            post_time = base_time - timedelta(days=value)
            return post_time.strftime('%Y-%m-%d')

        elif unit == '주':
            post_time = base_time - timedelta(weeks=value)
            return post_time.strftime('%Y-%m-00')  # 일자를 00으로

        elif unit == '달':
            post_time = base_time - relativedelta(months=value)
            return post_time.strftime('%Y-%m-00')

        elif unit == '년':
            post_time = base_time - relativedelta(years=value)
            return post_time.strftime('%Y-00-00')

        return None
        

if __name__ == "__main__":
    engine = create_engine(f"mysql+pymysql://{sys.argv[1]}:{sys.argv[2]}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")
    while True:
        print("1.중고나라", '\n', "2.번개장터", '\n', "3.종료", sep='')
        print("플랫폼을 선택하세요: ")
        platform = int(input())
        if platform == 3:
            break
        elif platform == 1:
            joongna_post_extractor = JoongnaPostInfoExtractor(engine)
            joongna_post_extractor.extract_postinfo()
        elif platform == 2:
            bunjang_post_extractor = BunjangPostInfoExtractor(engine)
            bunjang_post_extractor.extract_postinfo()