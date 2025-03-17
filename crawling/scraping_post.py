import traceback

import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session



class PostScraper:
    def __init__(self, product: str):
        self.product = product
        self.headers = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        self.post_list_by_id=set()

    def scrapJoongnaPost(self, session):
        errrorStack = 0
        for page_num in range(1,200):
            
            url = f"https://web.joongna.com/search/{self.product}?page={page_num}&sort=RECENT_SORT&productFilterType=APP&saleYn=SALE_Y"
            response = requests.get(url, headers=self.headers)

            parser = BeautifulSoup(response.text, 'html.parser')
            posts = parser.find('main').find('div', "w-full text").find('ul', "grid").find_all('li')
            
            if posts != None:
                for post in posts:
                    atag_post = post.find('a')
                    if (atag_post == None):
                        continue
                    post_identifier = atag_post['href'][9:]
                    self.post_list_by_id.add(int(post_identifier))  
            else:
                return
            
            for post_id in self.post_list_by_id:
                try:
                    session.execute(text(f"INSERT INTO POST (Product, SiteName, PostId) VALUES ('iPhone14', 'JoongNaSite', {post_id})"))
                    session.commit()
                except Exception as e:
                    errrorStack += 1
                    print(e)
                    if errrorStack == 10:
                        return
                    else:
                        continue
            self.post_list_by_id.clear()


    

    def get_posts(self):
        return self.posts


if __name__ == "__main__" :
    engine = create_engine("mysql+pymysql://uibo:1231@database-1.c12282e28jz4.ap-northeast-2.rds.amazonaws.com/JoonggoInfo")
    session = Session(bind=engine)
    
    post_scraper= PostScraper("iPhone14")
    post_scraper.scrapJoongnaPost(session=session)
    
    session.close()
    
    
