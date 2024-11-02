import time
import sys
import json
import threading
import requests
from bs4 import BeautifulSoup

done = False

# 스피너 함수
def spinner():
    while not done:
        for char in "/-\|":
            sys.stdout.write(f'\r{char}')  # 현재 위치에서 스피너를 출력
            sys.stdout.flush()
            time.sleep(0.1)

class PostCollector:
    def __init__(self, product:str):
        self.product = product
        self.header = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        self.posts=[]

    def collect_JoongNapost(self):
        for i in range(0, 6):    #  0~499999원 조건에서 검색, 500000~999999조건에서 검색, ```, 2500000~2999999조건에서 검색
            start_price = i * 500000
            end_price = (i + 1) * 500000 - 1
            for page_num in range(1,126):
                url = f"https://web.joongna.com/search/{self.product}?page={page_num}&minPrice={start_price}&maxPrice={end_price}&productFilterType=APP&saleYn=SALE_Y&sort=RECENT_SORT"
                response = requests.get(url, headers=self.header)
                response_body = response.text
                beautifulsoup = BeautifulSoup(response_body, 'html.parser')
                posts = beautifulsoup.find('main').find('div', "w-full text").find('ul', "grid").find_all('li')
                
                for post in posts:
                    post_atag = post.find('a')
                    if (post_atag == None):
                        continue
                    post_identifier = post_atag['href'][9:]
                    self.posts.append({"id":None, "keyword":self.product, "site_name":"JoongNa", "identifier":post_identifier})
    

    def get_posts(self):
        return self.posts


if __name__ == "__main__" :
    post_collector = PostCollector("iPhone14")
    spinner_thread = threading.Thread(target=spinner)
    collect_post_thread = threading.Thread(target=post_collector.collect_JoongNapost)
    spinner_thread.start()
    collect_post_thread.start()
    collect_post_thread.join()
    

    posts_json = json.dumps(post_collector.get_posts())
    response = requests.post(url="http://127.0.0.1:8000/post/", data=posts_json)
    print(response)
    done = True
    spinner_thread.join()
