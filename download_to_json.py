from collections import defaultdict, namedtuple, Counter
from datetime import date, timedelta
from multiprocessing import Pool
import json

from bs4 import BeautifulSoup
import requests


def download(url):
    """
    Download a file from a URL.
    Needs to be a top-level function to be used with the multiprocessing package (needs to be pickable).
    """
    page = requests.get(url)
    print('=', end='')
    return page


def planet_granite_scrape(start_date, days):
    """
    [TODO] embed/read into html?! https://stackoverflow.com/questions/7346563/loading-local-json-file
    [TODO] https://stackoverflow.com/questions/7431268/how-to-read-data-from-csv-file-using-javascript
    [TODO] split start time off
    [TODO] assert dates are the same, record day ot the week in a repeatable fashion
    [TODO] duration, assert same if there
    [TODO] reload at 00:01 (or 10pm + 2h ?!)

    datetime.datetime.strptime('Mon Feb 15 2010', '%a %b %d %Y').strftime('%d/%m/%Y')
    '15/02/2010'
    """

    print(''.join('_' if num % 10 else str(num // 10) for num in range(1, days + 1)))
    print(''.join(str(num % 10) for num in range(1, days + 1)))

    base_url = 'https://planetgranite.com/sv/calendar/{}/'
    date_strings = [(start_date + timedelta(days=after)).strftime("%Y-%m-%d") for after in range(days)]
    pages = map(download, (base_url.format(day_string) for day_string in date_strings))  # Pool(16).

    events = []
    event_counter = Counter()
    for day, page in zip(date_strings, pages):

        page_parser = BeautifulSoup(page.content, 'html.parser')
        for event_html in page_parser.select('.type-tribe_events'):

            desc = event_html.select_one('.tribe-events-list-event-title a').string
            cancelled = 'cancelled' in desc.lower()
            start = event_html.select_one('.tribe-event-date-start').string
            end = event_html.select_one('.tribe-event-time').string if '@' in start else 'ALL DAY'
            desc, start, end = map(lambda s: s.replace('**', '').strip(), (desc, start, end))
            title, *spec = (s.strip() for s in desc.split('–'))
            specs = '-'.join(spec)
            category_classes = filter(lambda s: 'category' in s, event_html.attrs['class'])
            categories = sorted([attr.split('-')[-1] for attr in category_classes])
            recurring = event_html.select_one('.event-is-recurring a')
            recurring = recurring.attrs['href'] if recurring else None
            link = event_html.select_one('.summary a').attrs['href']
            group_index = event_counter[title.lower()]

            events.append((title, cancelled, categories, day, start, end, specs, recurring, link, group_index))
            event_counter[title.lower()] +=1

    event = namedtuple('Event', 'index title cancelled categories day start end specs '
                                'recurring link group_index group_count'.split())
    events = [event(index, *details, event_counter[details[0].lower()]) for index, details in enumerate(events)]

    with open('events.json', 'w') as json_file_out:
        json.dump(events, json_file_out, indent=4)

    # sorted(events, key=lambda d: ('events' not in events[d][0][1], events[d][0][1], events[d][0][0]))


if __name__ == '__main__':
    planet_granite_scrape(date.today(), days=3)
