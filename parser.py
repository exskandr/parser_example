import requests
from bs4 import BeautifulSoup
import csv
import os


HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0',
           'accept': '*/*'}
HOST = 'https://auto.ria.com'
FILE = 'cars.csv'


#  створення запиту на сервер
def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


# отримання кількість сторінок для парсінгу
def get_pages_count(html):
    soup = BeautifulSoup(html, 'html.parser')
    pagination = soup.find_all('span', class_='mhide')
    if pagination:
        return int(pagination[-1].get_text())
    else:
        return 1


# сам парсінг
def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = soup.find_all('div', class_='proposition')

    cars = []
    for item in items:
        uah_price = item.find('span', class_='grey size13')
        if uah_price:
            uah_price = uah_price.get_text().replace(' • ', '')
        else:
            uah_price = 'ціну потрібно уточняти'
        cars.append({
           'title': item.find('div', class_='proposition_title').get_text(strip=True),
            'link': HOST + item.find('a').get('href'),
            'usd_price': item.find('span', class_='green').get_text(strip=True),
            'uah_price': uah_price,
            'city': item.find('div', class_='proposition_region').find_next('strong').get_text(strip=True),
        })
    return cars


# сворення файла для зберігання данних
def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Марка авто', 'Посилання', 'Ціна $', 'Ціна UAH', 'Місто'])
        for item in items:
            writer.writerow([item['title'], item['link'], item['usd_price'], item['uah_price'], item['city']])


# основний скрипт для роботи
def parse():
    MARKA = input('Введіть марку авто')
    URL = f'https://auto.ria.com/uk/newauto/marka-{MARKA}/'
    #URL = input('Введіть адресу URL: ')
    #URL = URL.strip()
    html = get_html(URL)
    if html.status_code == 200:
        cars = []
        pages_count = get_pages_count(html.text)
        for page in range(1, pages_count + 1):
            print(f'Парсинг страницы {page} из {pages_count}...')
            html = get_html(URL, params={'page': page})
            cars.extend(get_content(html.text))
        save_file(cars, FILE)
        print(f'Отримано {len(cars)} автомобілів')
        os.startfile(FILE)
    else:
        print('error')


parse()