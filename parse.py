from datetime import date, timedelta

from bs4 import BeautifulSoup
import requests


def PG_scrape(starting_date, days):

    event_types = {'yoga', 'fitness', 'community-events', 'climbing', 'kids'}  # class: 'tribe-events-category-' + name

    current_date = starting_date
    for _ in range(days):

        url = f'https://planetgranite.com/sv/calendar/{current_date.strftime("%Y-%m-%d")}/'

        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        for event in soup.select('.type-tribe_events'):

            desc = event.select_one('.tribe-events-list-event-title a').string
            start = event.select_one('.time-details .tribe-event-date-start').string
            end = event.select_one('.time-details .tribe-event-time').string if '@' in start else 'ALL DAY'
            desc, start, end = map(lambda s: s.strip(), (desc, start, end))
            print(f'{desc:55s} [{start} -- {end}]')

            # event_type = list(s.split('-')[-1] for s in filter(lambda s: 'category' in s, event.attrs['class']))[0]

        current_date += timedelta(days=1)
        print()


if __name__ == '__main__':
    PG_scrape(date.today(), days=30)
