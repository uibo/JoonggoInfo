import os
from dotenv import load_dotenv
import traceback
import json
import re
import random
import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from abc import ABC, abstractmethod
from enum import Enum

from bs4 import BeautifulSoup
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

from ORM import Post, PostInfo, Pending_Post

class Level(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"

CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--log-level=3",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-infobars",
    "--disable-browser-side-navigation",
    "--disable-features=VizDisplayCompositor",
]

def create_chrome_driver():
    options = Options()
    for opt in CHROME_OPTIONS:
        options.add_argument(opt)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

class PostInfoExtractor(ABC):
    def __init__(self, engine, site, batch_size=100):
        self.engine = engine
        self.site = site
        self.batch_size = batch_size

    def select_pending_posts(self):
        with Session(self.engine) as session:
            pending_posts = list(session.execute(select(Pending_Post).where(Pending_Post.site == self.site).limit(self.batch_size)).scalars().all())
        return pending_posts
    
    def insert_postinfo(self, rows: list) -> bool:
        with Session(self.engine) as session:
            session.add_all(rows)
            session.commit()
        print(f"✅[{Level.INFO}] site={self.site} postinfo {len(rows)}개 삽입")
        return True
    
    def update_deleted_posts(self, deleted_posts: list) -> bool:
        with Session(self.engine) as session:
            for post in deleted_posts:
                session.execute(update(Post).where(Post.id==post.id).values(is_deleted=1))
            session.commit()
        print(f"⭕[{Level.INFO}] site={self.site}, {len(deleted_posts)}개 삭제된 게시글로 처리")
        return True

    @abstractmethod
    def extract_postinfo(self):
        raise NotImplementedError

    @abstractmethod
    def process_all_own_posts(self):
        raise NotImplementedError
    
class JoongnawebPostInfoExtractor(PostInfoExtractor):
    def __init__(self, engine, batch_size):
        super().__init__(engine, 'joongnaweb' ,batch_size)
        
    def select_pending_posts(self):
        return super().select_pending_posts()
    
    def insert_postinfo(self, rows):
        return super().insert_postinfo(rows)

    def update_deleted_posts(self, deleted_posts):
        return super().update_deleted_posts(deleted_posts)

    def extract_postinfo(self, pending_posts: list) -> tuple[list, list]:
        deleted_posts = list()
        rows = list()     
        for post in pending_posts:
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
                rows.append(PostInfo(post_id = post.id, title = title, content = content, price = price, uploaddate = uploaddate, status = status, location = location, imgurl = imgurl))
            except Exception as e:
                print(f"⭕[{Level.INFO}] site={self.site}, url={url} 현재 게시글 정보 추출 실패. 삭제됨")
                print(traceback.format_exc())
                deleted_posts.append(post)
        return rows, deleted_posts

    def process_all_own_posts(self):
        while True:
            pending_posts = self.select_pending_posts()
            if not pending_posts: # 더 이상 처리할 데이터가 없으면 반복문 종료
                break
            rows, deleted_posts = self.extract_postinfo(pending_posts)
            if rows:
                self.insert_postinfo(rows)
            if deleted_posts:
                self.update_deleted_posts(deleted_posts)
        return
   
class BunjangPostInfoExtractor(PostInfoExtractor):
    xpath_dict = {'title': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div[1]',
              'content': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[1]/p',
              'price': '/html/body/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[1]/div[3]/div',
              'uploaddate': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div[1]/div/div[3]',
              'location': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[5]/div[1]/div/div[1]/div[2]/div[2]/div[1]/div[2]/div/span',
              'condition': '//*[@id="root"]/div/div/div[4]/div[1]/div/div[2]/div/div[2]/div/div[1]/div[2]/div[2]/div[1]/div[2]',
              'imgurl': '/html/body/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div[1]/div/div[1]/div/img[1]',
              'soldout_status': "/html/body/div[1]/div/div/div[4]/div[1]/div/div[2]/div/div[1]/div/div[1]/div[2]/div/img"}

    @staticmethod
    def parse_relative_time(text, base_time=None):
        if base_time is None:
            base_time = datetime.now()

        match = re.match(r'(\d+)\s*(분|시간|일|주|달|년) 전', text)
        if not match:
            return None

        value, unit = int(match.group(1)), match.group(2)

        if unit == '분':
            post_time = base_time - timedelta(minutes=value)
            return post_time.strftime('%Y-%m-%d')

        elif unit == '시간':
            post_time = base_time - timedelta(hours=value)
            return post_time.strftime('%Y-%m-%d')

        elif unit == '일':
            post_time = base_time - timedelta(days=value)
            return post_time.strftime('%Y-%m-%d')

        elif unit == '주':
            start_date = base_time - timedelta(weeks=value)
            end_date = base_time - timedelta(weeks=value-1)
            random_date = start_date + timedelta(days=random.randint(0, (end_date - start_date).days - 1))
            return random_date.strftime('%Y-%m-%d')

        elif unit == '달':
            start_date = base_time - relativedelta(months=value)
            end_date = base_time - relativedelta(months=value-1)
            # 랜덤 날짜 계산 (각 달의 일수에 따라)
            delta_days = (end_date - start_date).days
            random_date = start_date + timedelta(days=random.randint(0, delta_days - 1))
            return random_date.strftime('%Y-%m-%d')

        elif unit == '년':
            start_date = base_time - relativedelta(years=value)
            end_date = base_time - relativedelta(years=value-1)
            delta_days = (end_date - start_date).days
            random_date = start_date + timedelta(days=random.randint(0, delta_days - 1))
            return random_date.strftime('%Y-%m-%d')

        return None

    def __init__(self, engine, batch_size):
        super().__init__(engine, 'bunjang' ,batch_size)
    
    def select_pending_posts(self):
        return super().select_pending_posts()
    
    def insert_postinfo(self, rows):
        return super().insert_postinfo(rows)

    def update_deleted_posts(self, deleted_posts):
        return super().update_deleted_posts(deleted_posts)

    def extract_postinfo(self, pending_posts: list) -> tuple[list, list]:
        deleted_posts = list()
        rows = list()
        for post in pending_posts:
            url = f"https://m.bunjang.co.kr/products/{post.post_identifier}?original=1"
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
                conditions = [condition[0].text] if condition else []
                rows.append(PostInfo(post_id=post.id, title=title, content=content, price=price, uploaddate=uploaddate, status=status, location=location, url=url ,imgurl=imgurl, conditions=conditions))
            except Exception as e:
                print(f"⭕[{Level.INFO}] site={self.site}, url={url} 현재 게시글 정보 추출 실패. 삭제됨")
                print(traceback.format_exc())
                deleted_posts.append(post)
        return rows, deleted_posts

    def process_all_own_posts(self):
        try:
            self.driver = create_chrome_driver()
            self.driver.implicitly_wait(5)
            while True:
                pending_posts = self.select_pending_posts()
                if not pending_posts: # 더 이상 처리할 데이터가 없으면 반복문 종료
                    break
                rows, deleted_posts = self.extract_postinfo(pending_posts)
                if rows:
                    self.insert_postinfo(rows)
                if deleted_posts:
                    self.update_deleted_posts(deleted_posts)
        finally:
            self.driver.quit()
        return

class JoongnacafePostInfoExtractor(PostInfoExtractor):
    def __init__(self, engine, batch_size=100):
        super().__init__(engine, 'joongnacafe', batch_size)

    def select_pending_posts(self):
        return super().select_pending_posts()
    
    def insert_postinfo(self, rows):
        return super().insert_postinfo(rows)

    def update_deleted_posts(self, deleted_posts):
        return super().update_deleted_posts(deleted_posts)

    def extract_postinfo(self, pending_posts: list) -> tuple[list, list]:
        deleted_posts = list()
        rows = list()
        for post in pending_posts:
            url = f"https://cafe.naver.com/ArticleRead.nhn?clubid=10050146&articleid={post.post_identifier}"
            self.driver.get(url)
            try:
                iframe_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "cafe_main")))
                self.driver.switch_to.frame(iframe_element)

                # postinfo 추출
                title_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'title_text')))
                title = title_element.text
                uploaddate = self.driver.find_element(By.CLASS_NAME, 'date').text
                price = int(self.driver.find_element(By.CLASS_NAME, "cost").text.replace('원','').replace(',',''))
                imgurl = self.driver.find_element(By.CLASS_NAME, 'image').get_attribute('src')
                components = self.driver.find_elements(By.CLASS_NAME, 'se-component-content')
                content = ''.join(p_tag.text for component in components for p_tag in component.find_elements(By.TAG_NAME, "p"))
                uploaddate = uploaddate[:-7]

                # 상품 상태 / 거래 지역
                commercial_detail = self.driver.find_elements(By.CLASS_NAME, 'CommercialDetail')
                conditions = []
                location = None
                if commercial_detail:
                    detail_text = commercial_detail[0].text
                    match = re.search(r'상품 상태\n([^\n]+)', detail_text)
                    if match:
                        conditions = [match.group(1)]
                    match = re.search(r'거래 지역\n([^\s\n]+)', detail_text)
                    if match:
                        location = match.group(1)

                # 판매 완료 여부
                sold_elements = self.driver.find_elements(By.CLASS_NAME, 'sold_area')
                status = 1 if sold_elements and sold_elements[0].text == '판매 완료' else 0

                rows.append(PostInfo(
                    post_id=post.id,
                    title=title,
                    content=content,
                    price=price,
                    uploaddate=uploaddate,
                    status=status,
                    location=location,
                    url=url,
                    imgurl=imgurl,
                    conditions=conditions
                ))

            except Exception as e:
                print(f"⭕[{Level.INFO}] site={self.site}, url={url} 현재 게시글 정보 추출 실패. 삭제됨")
                print(traceback.format_exc())
                deleted_posts.append(post)
            finally:
                self.driver.switch_to.default_content()
        return rows, deleted_posts
     
    def process_all_own_posts(self):
        try:
            self.driver = create_chrome_driver()
            while True:
                pending_posts = self.select_pending_posts()
                if not pending_posts:
                    break
                rows, deleted_posts = self.extract_postinfo(pending_posts)
                if rows:
                    self.insert_postinfo(rows)
                if deleted_posts:
                    self.update_deleted_posts(deleted_posts)
        finally:
            self.driver.quit()

if __name__ == "__main__":
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")

    # bunjangpostinfoextractor = BunjangPostInfoExtractor(engine, 100)
    # bunjangpostinfoextractor.process_all_own_posts()

    joongnacafepostinfoextractor = JoongnacafePostInfoExtractor(engine, 10)
    joongnacafepostinfoextractor.process_all_own_posts()

    # joongnawebpostinfoextractor = JoongnawebPostInfoExtractor(engine, 100)
    # joongnawebpostinfoextractor.process_all_own_posts()

