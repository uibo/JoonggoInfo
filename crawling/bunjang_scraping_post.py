from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import pandas as pd
import numpy as np

driver = webdriver.Chrome()
product_urls = open("macbookair_bunjang_urls.txt", "a") # 제품 이름_bunjang_urls.txt

# range = 제품 개수 / 100
for i in range(1, 700):
    # 제품 url - 현재 맥북에어
    url = f'https://m.bunjang.co.kr/search/products?order=score&page={i}&q=%EB%A7%A5%EB%B6%81%EC%97%90%EC%96%B4'
    # '%EB%A7%A5%EB%B6%81%ED%94%84%EB%A1%9C'
    driver.get(url)
    driver.implicitly_wait(100)
    for j in range(1, 101): # 번개장터 1페이지당 100개 제품
        link_xpath = f'//*[@id="root"]/div/div/div[4]/div/div[4]/div/div[{j}]/a'
        link = driver.find_element(By.XPATH, link_xpath)
        product_link = link.get_attribute("href")
        bunjang = product_link[:33]
        if bunjang == 'https://m.bunjang.co.kr/products/':
            product_urls.write(product_link + '\n')
        print(f"{(i - 1) * 100 + j}번째 제품 완료")
        driver.implicitly_wait(100)

driver.quit()
product_urls.close()