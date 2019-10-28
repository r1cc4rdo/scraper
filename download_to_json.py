from datetime import date, datetime, timedelta
from multiprocessing import Pool
import json
import re

from bs4 import BeautifulSoup
import requests

desc_parser = re.compile(r'(?:(.+?) – (.+?) \| (\d+) (?i:min))|(?:(.+?) – (.+))|(.+)')


def download(url):
    """
    Download a file from a URL.
    Needs to be a top-level function to be used with the multiprocessing package (needs to be pickable).
    """
    page = requests.get(url)
    print('=', end='')
    return page


def parse_description(desc):
    """
    Matches strings like: 'F10 Alpine – Alejandro | 60 min', 'Yin Yoga – Valeria' or 'Belay Lesson'.
    Returns a tuple of (title, instructor, duration). If instructor or duration are not set, defaults are '' and 0.
    """
    title, instructor, substitutes, duration = '*** MATCH FAILED ***', '', '', 0
    desc_match = desc_parser.match(re.sub(r"[*()]", "", desc))
    if desc_match:
        if desc_match.group(1):  # first pattern

            title, instructor, duration = (desc_match.group(index) for index in range(1, 4))

        elif desc_match.group(4):  # second pattern

                title, instructor, duration = desc_match.group(4), desc_match.group(5), 0

        else:  # third pattern

            title, instructor, duration = desc_match.group(6), '', 0

    sub_index = instructor.lower().find(' sub ')
    if sub_index != -1:
        instructor, substitutes = instructor[:sub_index], instructor[sub_index+5:]

    return title, instructor, substitutes, int(duration)


def planet_granite_scrape(start_date, days):

    print(''.join('_' if num % 10 else str(num // 10) for num in range(1, days + 1)))
    print(''.join(str(num % 10) for num in range(1, days + 1)))

    base_url = 'https://planetgranite.com/sv/calendar/{}/'
    dates = [start_date + timedelta(days=after) for after in range(days)]
    pages = Pool(16).map(download, (base_url.format(day.strftime("%Y-%m-%d")) for day in dates))

    events = ['title instructor substitutes cancelled dotw day month year '
              'hh mm duration_minutes categories recurring link'.split()]
    for event_date, page in zip(dates, pages):

        page_parser = BeautifulSoup(page.content, 'html.parser')
        for event_html in page_parser.select('.type-tribe_events'):

            ids = ('.tribe-events-list-event-title a', '.tribe-event-date-start')  # event description, start time
            desc, start_time_string = map(lambda s: ' '.join(event_html.select_one(s).string.split()), ids)

            title, instructor, substitutes, duration_from_desc = parse_description(desc)
            cancelled = 'cancelled' in title.lower()

            if '@' in start_time_string:

                dotw_month_day, hh_mm_ampm = map(lambda s: s.strip(), start_time_string.split('@'))
                end_hh_mm_ampm = event_html.select_one('.tribe-event-time').string.strip()
                start_time = datetime.combine(event_date, datetime.strptime(hh_mm_ampm, '%I:%M %p').time())
                end_time = datetime.combine(event_date, datetime.strptime(end_hh_mm_ampm, '%I:%M %p').time())

            else:

                dotw_month_day = start_time_string.strip()
                midnight = datetime.combine(event_date, datetime.min.time())
                start_time, end_time = midnight, midnight + timedelta(hours=24)

            duration_minutes = int((end_time - start_time).total_seconds()) // 60

            category_classes = filter(lambda s: 'category' in s, event_html.attrs['class'])
            categories = sorted([attr.split('-')[-1] for attr in category_classes])

            recurring = event_html.select_one('.event-is-recurring a')
            recurring = recurring.attrs['href'] if recurring else None
            link = event_html.select_one('.summary a').attrs['href']

            assert event_date.strftime('%a %B %-d') == dotw_month_day
            assert (duration_from_desc == 0) or (duration_from_desc == duration_minutes)

            dotw, year, month, day, hh, mm = start_time.strftime('%a %Y %B %d %H %M').split()
            events.append((title, instructor, substitutes, cancelled,
                           dotw, day, month, year, hh, mm, duration_minutes,
                           categories, recurring, link))

    with open('events.json', 'w') as json_file_out:
        json.dump(events, json_file_out, indent=4)


if __name__ == '__main__':
    planet_granite_scrape(date.today(), days=15)
