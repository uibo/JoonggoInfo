from dotenv import load_dotenv
import os
import re
from datetime import datetime
import calendar
from abc import ABC, abstractmethod
from enum import Enum


import requests
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pymysql.err import IntegrityError as pymysql_IntergrityError

from ORM import Post

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
]

def create_chrome_driver():
    options = Options()
    for opt in CHROME_OPTIONS:
        options.add_argument(opt)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

class BasePostExtractor(ABC):
    def __init__(self, engine):
        self.engine = engine

    @abstractmethod
    def extract_pids(self):
        raise NotImplementedError
    
    @abstractmethod
    def insert_posts(self):
        raise NotImplementedError
    
    @abstractmethod
    def process_all_pages(self):
        raise NotImplementedError

class JoongnawebPostExtractor(BasePostExtractor):
    def __init__(self, engine, product: str):
        super().__init__(engine)
        self.headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
        self.site = "joongnaweb"
        self.product = product
        self.url = f"https://web.joongna.com/search/{self.product}?sort=RECENT_SORT&productFilterType=APP&saleYn=SALE_Y"
        with Session(self.engine) as session:
            self.existing_pid_in_joongnaweb = set(session.execute(select(Post.post_identifier).where((Post.site == 'joongnaweb') & (Post.product == self.product))).scalars().all())

    def extract_pids(self, url) -> list[int]:
        pids = list()
        response = requests.get(url, headers=self.headers)
        parser = BeautifulSoup(response.text, 'html.parser')
        try:
            post_tags = parser.find('main').find('div', "w-full text").find('ul', "grid").find_all('li')
            if post_tags:
                for post_tag in post_tags:
                    post_atag = post_tag.find('a')
                    if (post_atag == None):
                        continue
                    post_identifier = post_atag['href'][9:]
                    pids.append(int(post_identifier))
                return pids
            else:
                return []
        except AttributeError as e:
            print(f"❌[{Level.WARNING}] site={self.site} 현재 page에서 게시글 추출 실패.")
            print(e)
            exit()


    def insert_posts(self, pids: list[int]) -> bool:
        with Session(self.engine) as session:
            buffer = []  # 임시로 보류 중인 post_identifier
            inserted_any = False

            for post_identifier in pids:
                if post_identifier not in self.existing_pid_in_joongnaweb:
                    # buffer에 있던 것도 함께 insert
                    for buffered_pid in buffer:
                        session.add(Post(site=self.site, post_identifier=buffered_pid, product=self.product))  # product는 필요시 수정
                    buffer.clear()

                    # 현재 pid도 insert
                    session.add(Post(site=self.site, post_identifier=post_identifier, product=self.product))
                    inserted_any = True
                else:
                    # 이미 존재하는 pid면 buffer에 보류
                    buffer.append(post_identifier)

            # 끝까지 반복해도 buffer가 남아있다면 => 이전 지점 도달로 간주 => insert하지 않음
            session.commit()
            print(f"✅post {len(pids)-len(buffer)}개 삽입")
            return inserted_any

    def process_all_pages(self):
        for page_num in range(1,200):
            url_to_be_processd = self.url + f"&page={page_num}"
            pids = self.extract_pids(url_to_be_processd)
            
            if pids:
                result = self.insert_posts(pids)
                if result:
                    continue
                else:
                    print(f"⭕[{Level.INFO}] site={self.site}, page_num={page_num} 삽입된 post_identifier 없음. 전부 이전에 크롤링한 것들.")
                    break
            else:
                print(f"⭕[{Level.INFO}] site={self.site}, 현재 page에 게시글 없음.")
                break
        return
    
class BunjangPostExtractor(BasePostExtractor):
    def __init__(self, engine, product):
        super().__init__(engine)
        self.site = "bunjang"
        self.product = product
        self.url = f"https://m.bunjang.co.kr/search/products?order=date&q={self.product}"
      
    def extract_pids(self, url: str) -> list[int]:
            pids = list()
            self.driver.get(url)
            for post_num in range(1, 101): # 번개장터 1페이지당 100개 제품
                try:
                    post_tag = self.driver.find_element(By.XPATH, f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{post_num}]/a')
                    post_identifier = post_tag.get_attribute("data-pid")
                    if post_identifier:
                        pids.append(int(post_identifier))
                except NoSuchElementException:
                    print(f"⭕[{Level.INFO}] site={self.site}, post_num={post_num} 현재 page의 더 이상 추출할 게시글 tag가 없음.")
                    break
            return pids

    def insert_posts(self, pids: list[int]) -> int:
        duplicate_count = 0
        for post_identifier in pids:
            with Session(self.engine) as session:
                try:
                    session.add(Post(product=self.product, site=self.site, post_identifier=post_identifier))
                    session.commit()
                except Exception as e:
                    duplicate_count += 1
                    session.rollback()
                    print(f"⭕[{Level.INFO}] site={self.site}, post_identifier={post_identifier} 중복 삽입 발생")
                    print(e)
                    if duplicate_count == 3:
                        inserted_post_count = pids.index(post_identifier) - 2
                        print(f"⭕[{Level.INFO}] site={self.site}, 중복 삽입 3회 발생. 이전 크롤링 지점 도달")
                        print(f"✅post {inserted_post_count}개 삽입")
                        return 0
        print(f"✅post {len(pids)-duplicate_count}개 삽입")
        return 1
    
    def process_all_pages(self):
        try:
            self.driver = create_chrome_driver()
            page_num = 0
            while True:
                page_num += 1
                url = self.url + f"&page={page_num}"
                pids = self.extract_pids(url)
                if pids: # 1개 이상의 post_identifier 추출 성공
                    if self.insert_posts(pids): #중복 삽입 3회 미만. 정상적인 삽입입
                        continue
                    else: # 이전 크롤링 지점 도달 
                        break 
                else: # 현재 page에 게시글 존재하지 않음.
                    print("pid 추출실패로 인한 종료")
                    print(f"⭕[{Level.INFO}] site={self.site}, 현재 page에 게시글 존재하지 않음. 초기삽입 완료")
                    break
        finally:
            self.driver.quit()

class JoongnacafePostExtractor(BasePostExtractor):
    def __init__(self, engine, product, encoded_product):
        super().__init__(engine)
        self.site = "joongnacafe"
        self.headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
        self.product = product
        self.url = f"https://cafe.naver.com/ArticleSearchList.nhn?search.clubid=10050146&search.menuid=339&search.media=0&search.exact=&userDisplay=50&search.option=0&search.sortBy=date&search.searchBy=0&search.searchBlockYn=0&search.includeAll=&search.viewtype=title&search.include=&search.exclude=%B8%C5%C0%D4+%B1%B3%C8%AF+%BB%F0%B4%CF%B4%D9+%B1%B8%B8%C5+%C3%D6%B0%ED%B0%A1&search.query={encoded_product}"  # + &search.searchdate=2024-03-012024-03-31&search.page=1"


    def extract_pids(self, url: str) -> list[int]:
        pids = list()
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        atags = soup.select("a.article")

        if atags:
            for atag in atags:
                post_url = atag.attrs['href']
                match = re.search(r"articleid=([^&]+)", post_url)
                article_id = int(match.group(1))
                pids.append(article_id)
            return pids
        else:
            return []
    
    def insert_posts(self, pids: list[int]):
        for post_identifier in pids:
            with Session(self.engine) as session:
                try:
                    session.add(Post(product=self.product, site=self.site, post_identifier=post_identifier))
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(f"❌[{Level.WARNING}] site={self.site} pid삽입중 예외발생")
                    print(e)
                    continue
        print(f"✅post {len(pids)}개 삽입")
        return 1

    @staticmethod
    def generate_month_ranges_until_previous(end_year, end_month):
        def get_range(year, month):
            last_day = calendar.monthrange(year, month)[1]
            return [f"{year:04d}-{month:02d}-01{year:04d}-{month:02d}-15", f"{year:04d}-{month:02d}-16{year:04d}-{month:02d}-{last_day}"]

        # 기준은 전달
        today = datetime.now()
        start_year = today.year
        start_month = today.month - 1
        if start_month == 0:
            start_month = 12
            start_year -= 1

        # 리스트 만들기 (거꾸로)
        result = []
        year, month = start_year, start_month
        while (end_year < year) or (end_year == year and end_month <= month):
            result.extend(get_range(year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return result

    def process_all_pages(self):
        print("중고나라카페 게시글 추출 종료 년월을 입력하세요 ex)2022 09: ")
        end_year, end_month = map(int, input().split())
        periods = JoongnacafePostExtractor.generate_month_ranges_until_previous(end_year, end_month)
        for period in periods:
            url_with_period = self.url + f"&search.searchdate={period}"
            for page_num in range(1,101):
                url_to_be_processed = url_with_period + f"&search.page={page_num}"
                pids = self.extract_pids(url_to_be_processed)
                if pids:
                    self.insert_posts(pids)
                else:
                    print(f"⭕[{Level.INFO}] site={self.site}, peroid={period}, page_num={page_num} 현재 period는 현재 page에서 끝.")
                    break

if __name__ == "__main__" :
    load_dotenv()
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")

    # bunjangpostExtractor = BunjangPostExtractor(engine, 'iPhone14')
    # bunjangpostExtractor.process_all_pages()
   
    # joongnacafapostextractor = JoongnacafePostExtractor(engine, 'iPhone14', '%BE%C6%C0%CC%C6%F914')
    # joongnacafapostextractor.process_all_pages()

    # joongnawebpostextractor = JoongnawebPostExtractor(engine, 'iPhone14')
    # joongnawebpostextractor.process_all_pages()

