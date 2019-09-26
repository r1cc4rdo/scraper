from datetime import date, timedelta

from bs4 import BeautifulSoup
import requests


def PG_scrape(starting_date, days):

    def calendar_urls(start_date, days):
        for after in range(days):
            calendar_date = start_date + timedelta(days=after)
            yield f'https://planetgranite.com/sv/calendar/{calendar_date.strftime("%Y-%m-%d")}/'

    for calendar_url in calendar_urls(starting_date, days):
        page = requests.get(calendar_url)
        page_parser = BeautifulSoup(page.content, 'html.parser')
        for event in page_parser.select('.type-tribe_events'):

            desc = event.select_one('.tribe-events-list-event-title a').string
            start = event.select_one('.time-details .tribe-event-date-start').string
            end = event.select_one('.time-details .tribe-event-time').string if '@' in start else 'ALL DAY'
            desc, start, end = map(lambda s: s.strip(), (desc, start, end))
            print(f'{desc:55s} [{start} -- {end}]')

            # event_type = list(s.split('-')[-1] for s in filter(lambda s: 'category' in s, event.attrs['class']))[0]

        print()


if __name__ == '__main__':
    PG_scrape(date.today(), days=30)
