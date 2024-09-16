import requests
from bs4 import BeautifulSoup



class UrlCollector:
    def __init__(self, product:str, unicode:str):
        self.product = product
        self.unicode = unicode
        self.header = {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
        self.post_urls=[]

    def collect_url(self):
        #0~499999원 조건에서 검색, 500000~999999조건에서 검색, ```, 2500000~2999999조건에서 검색
        for i in range(5):
            start_price = i * 500000
            end_price = (i + 1) * 500000 - 1

            for page_num in range(1,125):
                url = f"https://web.joongna.com/search/{self.product}?page={page_num}&minPrice={start_price}&maxPrice={end_price}&productFilterType=APP&saleYn=SALE_Y&sort=RECENT_SORT"
                response = requests.get(url, headers=self.headers)
                response_body = response.text
                beautifulsoup = BeautifulSoup(response_body, 'html.parser')
                posts = beautifulsoup.find('main').find('div', "w-full text").find('ul', "grid").find_all('li')

                for post in posts:
                    post_url = post.find('a')['href']
                    self.post_urls.append(post_url)

    def get_urls(self):
        return self.post_urls




if __name__ == "__main__" :
    url_collector = UrlCollector("iPhone14", "%EC%95%84%EC%9D%B4%ED%8F%B014")
    url_collector.collect_url()
    print(url_collector.get_urls)