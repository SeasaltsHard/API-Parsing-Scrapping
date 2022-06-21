from pymongo import MongoClient
from lxml import html
import requests
from pprint import pprint

from pymongo.errors import DuplicateKeyError

header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
          '98.0.4758.141 YaBrowser/22.3.4.731 Yowser/2.5 Safari/537.36'}

yandex_url = 'https://yandex.ru/news/'
lenta_url = 'https://lenta.ru/'


#                                                       ---Yandex News---

response = requests.get(yandex_url, headers=header)
dom = html.fromstring(response.text)

news_list = dom.xpath(
    "//div[contains(@class, 'mg-card mg-card_flexible-single mg-card_type_image mg-grid__item')]")
news = []
for objct in news_list:
    data = {}
    news_title = objct.xpath('.//h2//text()')
    source = objct.xpath('.//span/a/text()')
    link = objct.xpath('.//h2/a/@href')
    publication_time = objct.xpath(".//span[contains(@class, 'mg-card-source__time')]//text()")

    data['Title: '] = news_title
    data['Source: '] = source
    data['Link: '] = link
    data['Publication time: Today, at '] = publication_time

    news.append(data)


client = MongoClient('127.0.0.1', 27017)
db = client['users0104']

news_db = db.news

for dictionary in news:
    news_db.insert_one(dictionary)

for doc in news_db.find({}):
    pprint(doc)
