from bs4 import BeautifulSoup
import requests
from datetime import datetime
from datetime import date

url = "https://www.coingecko.com"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)

soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('tbody')
rows = table.find_all('tr')
coins = []
for row in rows:
    name = row.find('div', {
                    'class': "tw-block 2lg:tw-inline tw-text-xs tw-leading-4 tw-text-gray-500 dark:tw-text-moon-200 tw-font-medium"}).text.strip()
    price_dollarsign = row.find(
        'span', {'data-price-target': "price"}).text.strip()
    price = price_dollarsign.replace('$', '').replace(',', '')
    coins.append({'Date': date.today().strftime('%d/%m/%Y'), 'Time': datetime.now().strftime(
        "%H:%M:%S"), 'Name': name, 'Price': price})
print(coins)
