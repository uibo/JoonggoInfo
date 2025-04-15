from dotenv import load_dotenv
import os
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pymysql.err import IntegrityError as pymysql_IntergrityError

from ORM import Post

class BasePostExtractor(ABC):
    headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
    
    def __init__(self, engine, product: str):
        self.engine = engine
        self.product = product

    @abstractmethod
    def extract_post(self):
        raise NotImplementedError

class JoongnaPostExtractor(BasePostExtractor):
    def __init__(self, engine, product: str):
        super().__init__(engine, product)
        self.site = "joongnaweb"
        self.url = f"https://web.joongna.com/search/{self.product}?sort=RECENT_SORT&productFilterType=APP&saleYn=SALE_Y"

    def extract_post(self):
        for page_num in range(1,200):
            post_identifiers = list()
            current_url = self.url + f"&page={page_num}"
            response = requests.get(current_url, headers=self.headers)
            parser = BeautifulSoup(response.text, 'html.parser')
            post_tags = parser.find('main').find('div', "w-full text").find('ul', "grid").find_all('li')

            if post_tags:
                for post_tag in post_tags:
                    post_atag = post_tag.find('a')
                    if (post_atag == None):
                        continue
                    post_identifier = post_atag['href'][9:]
                    post_identifiers.append(int(post_identifier))
            else:
                print("초기 삽입 완완료")
                break
            
            # 게시글 목록을 나타내는 한 페이지에서만 post_identifer 추출하고 db에 삽입진행(중복된 identifier는 추출하지 않기 위한 작업순서)
            with Session(self.engine) as session:
                error_count = 0
                for post_identifier in post_identifiers:
                    try:
                        session.add(Post(product=self.product, site=self.site, post_identifier=post_identifier))
                        session.commit()
                    except (IntegrityError, pymysql_IntergrityError) as e:
                        error_count += 1
                        session.rollback()
                        if error_count == 3:
                            print("중복된 삽입 시도 3회 발생")
                            return
                print(f"✅post {len(post_identifiers)-error_count}개 삽입")

class BunjangPostExtractor(BasePostExtractor):
    def __init__(self, engine, product):
        super().__init__(engine, product)
        self.site = "bunjang"
        self.url = f"https://m.bunjang.co.kr/search/products?order=date&q={self.product}"
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # GUI 없이 실행
        chrome_options.add_argument("--no-sandbox")  # 샌드박스 모드 비활성화
        chrome_options.add_argument("--disable-dev-shm-usage")  # /dev/shm 사용 비활성화
        chrome_options.add_argument("--log-level=3") # 로그 수준을 낮춰 warning message 출력 제한
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
      
    def extract_post(self):
        page = 0
        while True:
            post_identifiers = list()
            page += 1
            url = self.url + f"&page={page}"
            self.driver.get(url)
            try:
                for post_num in range(1, 101): # 번개장터 1페이지당 100개 제품
                    post_tag = self.driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{post_num}]/a')
                    post_identifier = post_tag.get_attribute("data-pid")
                    if post_identifier:
                        post_identifiers.append(post_identifier)
            except NoSuchElementException:
                self.insert_post(post_identifiers)
                print("초기삽입완료")
                break
            if not self.insert_post(post_identifiers):
                break

    def insert_post(self, post_identifiers):
        with Session(self.engine) as session:
            error_count = 0
            for post_identifier in post_identifiers:
                try:
                    session.add(Post(product=self.product, site=self.site, post_identifier=post_identifier))
                    session.commit()
                except (IntegrityError, pymysql_IntergrityError) as e:
                    error_count += 1
                    session.rollback()
                    if error_count == 3:
                        print("중복된 삽입 시도 2회 발생")
                        return 0
            print(f"✅post {len(post_identifiers)-error_count}개 삽입")
            return 1
                
if __name__ == "__main__" :
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")
    while True:
        print("1.중고나라", '\n', "2.번개장터", '\n', "3.종료", sep='')
        print("플랫폼을 선택하세요: ")
        platform = int(input())
        if platform == 1:
            joongna_post_extractor = JoongnaPostExtractor(engine, "iPhone14")
            joongna_post_extractor.extract_post()
        elif platform == 2:
            bunjang_post_extractor = BunjangPostExtractor(engine, "iPhone14")
            bunjang_post_extractor.extract_post()
        elif platform == 3:
            break