from datetime import date, timedelta
from collections import defaultdict
from multiprocessing import Pool

from bs4 import BeautifulSoup
import requests

# [TODO] html/markdown output, write with dates
# [TODO] refresh with lambda


def download(url):
    page = requests.get(url)
    print('=', end='')
    return page


def calendar_urls(start_date, days):
    print(''.join('_' if num % 10 else str(num // 10) for num in range(1, days + 1)))
    print(''.join(str(num % 10) for num in range(1, days + 1)))
    for after in range(days):
        calendar_date = start_date + timedelta(days=after)
        yield f'https://planetgranite.com/sv/calendar/{calendar_date.strftime("%Y-%m-%d")}/'


def planet_granite_scrape(starting_date, days):

    pages = Pool(16).map(download, calendar_urls(starting_date, days))
    events = defaultdict(list)
    for page in pages:

        page_parser = BeautifulSoup(page.content, 'html.parser')
        for event in page_parser.select('.type-tribe_events'):

            desc = event.select_one('.tribe-events-list-event-title a').string
            if 'cancelled' in desc.lower():
                continue

            start = event.select_one('.tribe-event-date-start').string
            end = event.select_one('.tribe-event-time').string if '@' in start else 'ALL DAY'
            desc, start, end = map(lambda s: s.strip(), (desc, start, end))
            categories = [attr.split('-')[-1] for attr in filter(lambda s: 'category' in s, event.attrs['class'])]
            link = event.select_one('.event-is-recurring a')  # [TODO] lift link from summary
            title, *spec = (s.strip() for s in desc.split('–'))
            specs = '-'.join(spec)

            print(f'{desc:55s} [{start:24} -- {end:8}]')
            events[title.lower()].append((title, categories, start, end, specs, link))

        print()

    for desc in sorted(events):
        print(f'{events[desc][0][0]}')  # original title
        for title, categories, start, end, specs, link in events[desc]:
            print(f'\t {" " if link else "*"} {start:24} -- {end:8}   \t{specs}   \t[{" ".join(categories)}]   \t{link}')
        print()


if __name__ == '__main__':
    planet_granite_scrape(date.today(), days=30)
