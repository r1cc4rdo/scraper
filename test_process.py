from multiprocessing import Process, Manager
from datetime import date, timedelta

import requests


def download(url, pages):
    pages[url] = requests.get(url)
    print('.', end='')


def calendar_urls(start_date, days):
    print(''.join('_' if num % 10 else str(num // 10) for num in range(1, days + 1)))
    print(''.join(str(num % 10) for num in range(1, days + 1)))
    for after in range(days):
        calendar_date = start_date + timedelta(days=after)
        yield f'https://planetgranite.com/sv/calendar/{calendar_date.strftime("%Y-%m-%d")}/'


pages = Manager().dict()
processes = [Process(target=download, args=(url, pages)) for url in calendar_urls(date.today(), days=15)]
for process in processes:
    process.start()
for process in processes:
    process.join()

print('Ciao')