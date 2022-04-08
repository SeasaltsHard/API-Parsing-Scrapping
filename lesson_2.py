from bs4 import BeautifulSoup as bs
import requests


def parser_superjob(vacancy):
    vacancy_data = []

    params = {
        'keywords': vacancy,
        'profession_only': '1',
        'geo[c][0]': '15',
        'geo[c][1]': '1',
        'geo[c][2]': '9',
        'page': ''
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29'
    }

    link = 'https://www.superjob.ru/vacancy/search/'

    html = requests.get(link, params=params, headers=headers)

    if html.ok:
        parsed_html = bs(html.text, 'lxml')

        page_block = parsed_html.find('a', {'class': 'f-test-button-1'})
    if not page_block:
        last_page = 1
    else:
        page_block = page_block.findParent()
        last_page = int(page_block.find_all('a')[-2].getText())

    for page in range(0, last_page + 1):
        params['page'] = page
        html = requests.get(link, params=params, headers=headers)

        if html.ok:
            parsed_html = bs(html.text, 'html.parser')
            vacancy_items = parsed_html.find_all('div', {'class': 'f-test-vacancy-item'})

            for item in vacancy_items:
                vacancy_data.append(parser_item_superjob(item))

    return vacancy_data


def parser_item_superjob(item):
    vacancy_data = {}

    vacancy_name = item.find_all('a')
    if len(vacancy_name) > 1:
        vacancy_name = vacancy_name[-2].getText()
    else:
        vacancy_name = vacancy_name[0].getText()
    vacancy_data['vacancy_name'] = vacancy_name

    # salary
    salary = item.find('span', {'class': 'f-test-text-company-item-salary'}).findChildren()
    if not salary:
        salary_min = None
        salary_max = None
        salary_currency = None
    else:
        salary_currency = salary[-1].getText()
        is_check_salary = item.find('span', {'class': 'f-test-text-company-item-salary'}).getText().replace(
            u'\xa0', u' ').split(' ', 1)[0]
        if is_check_salary == 'до' or len(salary) == 2:
            salary_min = None
            salary_max = int(salary[0].getText().replace(u'\xa0', u''))
        elif is_check_salary == 'от':
            salary_min = int(salary[0].getText().replace(u'\xa0', u''))
            salary_max = None
        else:
            salary_min = int(salary[0].getText().replace(u'\xa0', u''))
            salary_max = int(salary[2].getText().replace(u'\xa0', u''))

    vacancy_data['salary_min'] = salary_min
    vacancy_data['salary_max'] = salary_max
    vacancy_data['salary_currency'] = salary_currency

    # link
    vacancy_link = item.find_all('a')

    if len(vacancy_link) > 1:
        vacancy_link = vacancy_link[-2]['href']
    else:
        vacancy_link = vacancy_link[0]['href']

    vacancy_data['vacancy_link'] = f'https://www.superjob.ru{vacancy_link}'

    vacancy_data['site'] = 'www.superjob.ru'
    return vacancy_data
