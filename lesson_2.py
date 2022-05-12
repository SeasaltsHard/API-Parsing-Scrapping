import requests
from bs4 import BeautifulSoup as bs
import json
#                                         ---Url and header info---


header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                        '98.0.4758.141 YaBrowser/22.3.2.628 Yowser/2.5 Safari/537.36'}
base_url = 'https://hh.ru/'
suffix = 'search/vacancy?L_profession_id=29.8&area=1&no_magic=true&' \
                 f'text=Программист+Python&hhtmFromLabel=rainbow_profession&items_on_page=20'
postfix = '&hhtmFrom=main'
url = base_url + suffix + postfix
response = requests.get(url, headers=header)
dom = bs(response.text, 'html.parser')

#                                     ---Getting the last page number---
last_page = int
for last_page in dom.find_all('a', {'data-qa': 'pager-page'}):    # Get all page objects.
    last_page = int(last_page.get_text())                         # Get last page number.

#                             ---Creating .html files and scraping them one by one---

page = 0
while page <= last_page:
    url_page = f'&page={page}'
    pager_url = base_url + suffix + url_page + postfix
    response = requests.get(pager_url, headers=header)
    with open('content.html', 'w', encoding='utf-8') as html_page:
        html_page.write(response.text)

    with open('content.html', 'r', encoding='utf-8') as html_page:
        content = html_page.read()
        dom = bs(content, 'html.parser')
        jobs = dom.find_all('div', {'class': 'vacancy-serp-item'})
        job_list = []
        for job in jobs:
            job_data = {}
            names = job.find('span', {'class': 'g-user-content'}).get_text()
            company_name = job.find('div', {
                'class': 'vacancy-serp-item__meta-info-company'}).get_text().replace('\xa0', ' ')
            link = job.find('a', {'class': 'bloko-link'})['href']

#                                       ---Entering the salary problem---

            if job.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}) is None:
                job_data['Salary: '] = None
            elif job.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}) is not None:
                salary = job.find('span', {
                    'data-qa': 'vacancy-serp__vacancy-compensation'}).get_text().replace('\u202f', ' ').split()
                if 'от' in salary:
                    job_data['Min. wage: '] = salary[1] + salary[2]
                    job_data['Currency: '] = salary[-1]
                elif 'до' in salary:
                    job_data['Max. wage: '] = salary[1] + salary[2]
                    job_data['Currency: '] = salary[-1]
                elif '–' in salary:
                    job_data['Min. wage: '] = salary[0] + salary[1]
                    job_data['Max. wage: '] = salary[3] + salary[4]
                    job_data['Currency: '] = salary[-1]

            job_data['Vacancy name: '] = names
            job_data['Company name: '] = company_name
            job_data['Link: '] = link
            job_list.append(job_data)
            with open('job_data.json', 'w', encoding='utf-8') as data:
                json.dump(job_list, data)
    page += 1
