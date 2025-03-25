import sys

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from pymysql.err import IntegrityError as pymysql_IntergrityError

from ORM import Post

class PostExtractor:
    def __init__(self, product: str):
        self.product = product
        self.site = "joongnaweb"
        self.headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        self.url = f"https://web.joongna.com/search/{self.product}?sort=RECENT_SORT&productFilterType=APP&saleYn=SALE_Y"

    def extract_post(self, session):
        for page_num in range(1,200):
            post_identifiers = set()
            current_url = self.url + f"&page={page_num}"
            response = requests.get(current_url, headers=self.headers)
            parser = BeautifulSoup(response.text, 'html.parser')
            posts = parser.find('main').find('div', "w-full text").find('ul', "grid").find_all('li')

            if posts:
                for post in posts:
                    atag_post = post.find('a')
                    if (atag_post == None):
                        continue
                    post_identifier = atag_post['href'][9:]
                    post_identifiers.add(int(post_identifier))
            else:
                print("초기 삽입 완료료")
                return
            
            # 게시글 목록을 나타내는 한 페이지에서만 post_identifer 추출하고 db에 삽입진행(중복된 identifier는 추출하지 않기 위한 작업순서)
            error_count = 0
            for post_identifier in post_identifiers:
                try:
                    post = Post(product=self.product, site=self.site, post_identifier=post_identifier)
                    session.add(post)
                    session.commit()
                except (IntegrityError, pymysql_IntergrityError) as e:
                    error_count += 1
                    if error_count == 2:
                        print("중복된 삽입 시도 2회 발생")
                        return

if __name__ == "__main__" :
    engine = create_engine(f"mysql+pymysql://{sys.argv[1]}:{sys.argv[2]}@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/joonggoinfo")
    session = Session(bind=engine)
    post_scraper = PostExtractor("iPhone14")
    post_scraper.extract_post(session=session) 
    session.close()