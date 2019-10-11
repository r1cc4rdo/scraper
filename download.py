from datetime import date, timedelta
from collections import defaultdict
from multiprocessing import Pool

from bs4 import BeautifulSoup
import requests

# [TODO] refresh with lambda (1 mo every 15 days) https://github.com/mixu/markdown-styles-lambda https://github.com/mixu/ghost-render https://github.com/mixu/markdown-styles
# [TODO] save log


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
    with open('event_by_date.md', 'w') as markdown_out:
        for page in pages:

            markdown_out.write(f'## {tuple(filter(lambda x: x, page.url.split("/")))[-1]}\n')
            page_parser = BeautifulSoup(page.content, 'html.parser')
            for event in page_parser.select('.type-tribe_events'):

                desc = event.select_one('.tribe-events-list-event-title a').string
                if 'cancelled' in desc.lower():
                    continue

                start = event.select_one('.tribe-event-date-start').string
                end = event.select_one('.tribe-event-time').string if '@' in start else 'ALL DAY'
                desc, start, end = map(lambda s: s.strip(), (desc, start, end))
                title, *spec = (s.strip() for s in desc.split('–'))
                specs = '-'.join(spec)
                categories = [attr.split('-')[-1] for attr in filter(lambda s: 'category' in s, event.attrs['class'])]
                recurring = event.select_one('.event-is-recurring a')
                recurring = recurring.attrs['href'] if recurring else None
                link = event.select_one('.summary a').attrs['href']

                markdown_out.write(f'1. [{"" if recurring else "**"}{start:24} -- {end:8} {desc:55s}{"" if recurring else "**"}]({link})\n')
                events[title.lower()].append((title, categories, start, end, specs, recurring, link))

    with open('event_by_type.md', 'w') as markdown_out:
        for desc in sorted(events):
            markdown_out.write(f'## {events[desc][0][0]} ({" ".join(events[desc][0][1])})\n')
            for title, categories, start, end, specs, recurring, link in events[desc]:
                markdown_out.write(f'1. [{"" if recurring else "**"}{start:24} -- {end:8} {specs}{"" if recurring else "**"}]({link})\n')


if __name__ == '__main__':
    planet_granite_scrape(date.today(), days=30)
