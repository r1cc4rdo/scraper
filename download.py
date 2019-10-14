from datetime import date, timedelta
from collections import defaultdict
from multiprocessing import Pool

from bs4 import BeautifulSoup
import requests


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
                desc, start, end = map(lambda s: s.replace('**', '').strip(), (desc, start, end))
                title, *spec = (s.strip() for s in desc.split('–'))
                specs = '-'.join(spec)
                categories = sorted([attr.split('-')[-1] for attr in filter(lambda s: 'category' in s, event.attrs['class'])])
                recurring = event.select_one('.event-is-recurring a')
                recurring = recurring.attrs['href'] if recurring else None
                link = event.select_one('.summary a').attrs['href']

                bold = "" if recurring else "**"
                markdown_out.write(f'1. [{bold}{start} -- {end} {desc}{bold}]({link})\n')
                events[title.lower()].append((title, categories, start, end, specs, recurring, link))

        markdown_out.write(f'---\n*Last updated: {date.today()}*\n')

    with open('event_by_type.md', 'w') as markdown_out:
        for desc in sorted(events, key=lambda d: ('events' not in events[d][0][1], events[d][0][1], events[d][0][0])):

            markdown_out.write(f'## {events[desc][0][0]} ({" ".join(events[desc][0][1])})\n')
            for title, categories, start, end, specs, recurring, link in events[desc]:
                link_text = f'{start} -- {end} {specs}'
                bold = "" if recurring else "**"
                markdown_out.write(f'1. [{bold}{link_text.strip()}{bold}]({link})\n')

        markdown_out.write(f'---\n*Last updated: {date.today()}*\n')


if __name__ == '__main__':
    planet_granite_scrape(date.today(), days=15)
