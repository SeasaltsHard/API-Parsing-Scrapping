from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
from pymongo import MongoClient
from pprint import pprint
import time


client = MongoClient('localhost',27017)
db = client['vacancies_db']
hh_vac = db.hh_vac
sj_vac = db.sj_vac


def hh_search(text, page, only_new = 'yes', hh_vac = hh_vac):

    user_agent = {'User-agent': 'Mozilla/5.0'}
    link_hh = ('https://hh.ru/search/vacancy?area=2&st=searchVacancy@enable_snippets=true&')
    #main_link = ('localhost/hh.html/')
    i = 0
    vacs = []

    for p in range(page):
        html = requests.get(f'{link_hh}&text={text}&page={p}',  headers = user_agent).text
        parsed_html = bs(html,'lxml')
        vac_list = parsed_html.findAll('div', {'class':'vacancy-serp-item__row vacancy-serp-item__row_header'})
        df = pd.DataFrame(columns=['name', 'salary_min', 'salary_max', 'url', 'site'])

        for vac in vac_list:
            #print(i)
            vac_data = {}

            main_info = vac.findChild()
            link = vac.find('a')
            if not link:
                url = 'nan'
                vac_data['name'] = ''
            else:
                vac_data['name'] = link.getText()
                url = link["href"].split('?')[0]
                vac_num = url.split('/')[3]



            compensation = vac.findParent().find('div', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            salary = 0
            salary_min = float('nan')
            salary_max = float('nan')
            if not compensation:
                pass
            else:
                salary = compensation.getText()
                salary = re.sub(r"\s+", "", salary)
                if salary.find('от') >= 0 :
                    salary_min = int(re.findall(r'\d+',  salary)[0])

                elif salary.find('до') >= 0 :
                    salary_max = int(re.findall(r'\d+', salary)[0])

                elif salary.find('-') >= 0 :
                    salary = re.findall(r'\d+', salary)
                    salary_min = salary[0]
                    salary_max = salary[1]

                #print('sal', salary)
                #print('salary_min', salary_min)
                #print('salary_max', salary_max)
                vac_data['salary_min'] = salary_min
                vac_data['salary_max'] = salary_max
                vac_data['url'] = url
                vac_data['vac_num'] = vac_num
                vac_data['site'] = 'HeadHunter'

                vacs.append(vac_data)
                df.append(vac_data, ignore_index = True)
                if only_new == 'yes':
                  if find_in_db('hh', vac_num) == 0:
                    hh_vac.insert_one(vac_data)
                else:
                  # Не слишком продуктивно писать в базу по одной, зато доп. задержка для сайта
                  hh_vac.insert_one(vac_data)


            i += 1
            time.sleep(1)
    return(vacs)

def sj_search(text, page, only_new = 'yes', sj_vac = sj_vac):



    user_agent = {'User-agent': 'Mozilla/5.0'}
    link_sj = ('https://www.superjob.ru/vacancy/search/?')
    #main_link = ('localhost/hh.html/')
    i = 0
    vacs = []
    url_start = 'https://www.superjob.ru'

    for p in range(1, page+1):
        html = requests.get(f'{link_sj}&keywords={text}&page={p}', headers = user_agent).text
        parsed_html = bs(html,'lxml')
        vac_list = parsed_html.findAll('div', {'class':'_3syPg _1_bQo _2FJA4'})
        df = pd.DataFrame(columns=['name', 'salary_min', 'salary_max', 'url', 'site'])

        for vac in vac_list:
            #print(i)
            vac_data = {}

            main_info = vac.findChild()
            #print('main_info', main_info)
            name = vac.find('div', {'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).getText()
            vac_data['name'] = name
            link = vac.find('a')

            if not link:
                url = 'nan'
                vac_num = 'nan'

            else:
                url_vac = link['href']
                url = f'{url_start}/{url_vac}'
                vac_data['url'] = url
                vac_data['vac_num'] = url

            salary = 0
            salary_min = float('nan')
            salary_max = float('nan')
            compensation = vac.find('span', {'class': '_3mfro _2Wp8I f-test-text-company-item-salary PlM3e _2JVkc _2VHxz'})
            if not compensation:
                salary = 0
            else:
                salary = compensation.getText()
                if salary.find('от') >= 0:
                    salary_min = re.findall(r'\d+', salary)[0]

                #elif salary.find('до') >= 0:
                    #salary_max = re.findall(r'\d+', salary)[0]
                elif salary.find('—') >= 0:
                    salary = re.findall(r'\d+', salary)

                    salary_min = int(salary[0])*1000
                    salary_max = int(salary[2])*1000
                elif salary.find('договорённости') >= 0:
                    salary_min = 'по договорённости'


            vac_data['salary_min'] = salary_min
            vac_data['salary_max'] = salary_max
            vac_data['url'] = url
            vac_data['vac_num'] = url
            vac_data['site'] = 'Superjob'

            vacs.append(vac_data)
            df.append(vac_data, ignore_index=True)
            if only_new == 'yes':
                if find_in_db('sj', url) == 0:
                    sj_vac.insert_one(vac_data)
            else:
                # Не слишком продуктивно писать в базу по одной, зато доп. задержка для сайта
                sj_vac.insert_one(vac_data)


            vacs.append(vac_data)
            df.append(vac_data, ignore_index=True)
            i += 1
    return (vacs)

           #df.append(vac_data, ignore_index = True)

def find_in_db(site, vac_num):
  exists = 0
  if site == 'hh':
    exists = hh_vac.count_documents({'vac_num': vac_num})
  return exists

def find_salary():
  salary = input('Введите минимальную зарплату: ')
  expensive_vacs = hh_vac.find({'salary_min':{'$gte':salary}}).sort('salary_min')
  print('Вакансии с зарплатой выше чем ', salary)
  for item in expensive_vacs:
    pprint(item)

find_salary()