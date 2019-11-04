from datetime import date, datetime, timedelta
from multiprocessing.pool import ThreadPool as Pool  # not "from multiprocessing import Pool" because AWS Lambda
import json
import re

from bs4 import BeautifulSoup
import requests

desc_parser = re.compile(r'(?:(.+?)–(.+?) (?:\| )*(\d+) (?i:min))|(?:(.+?)–(.+))|(.+)')


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

    title, instructor, substitutes = map(lambda s: s.strip(), (title, instructor, substitutes))
    return title, instructor, substitutes, int(duration)


def planet_granite_scrape(start_date, days, debug=False):

    print(''.join('_' if num % 10 else str(num // 10) for num in range(1, days + 1)))
    print(''.join(str(num % 10) for num in range(1, days + 1)))

    base_url = 'https://planetgranite.com/sv/calendar/{}/'
    dates = [start_date + timedelta(days=after) for after in range(days)]
    map_function = map if debug else Pool(processes=16).map  # cannot debug multi-process
    pages = map_function(download, (base_url.format(day.strftime("%Y-%m-%d")) for day in dates))

    events = ['title instructor substitutes cancelled start_epoch end_epoch categories recurring link'.split()]
    for event_date, page in zip(dates, pages):

        page_parser = BeautifulSoup(page.content, 'html.parser')
        for event_html in page_parser.select('.type-tribe_events'):

            ids = ('.tribe-events-list-event-title a', '.tribe-event-date-start')  # event description, start time
            desc, start_time_string = map(lambda s: ' '.join(event_html.select_one(s).string.split()), ids)

            title, instructor, substitutes, duration_from_desc = parse_description(desc)
            cancelled = 'cancelled' in desc.lower()

            if '@' in start_time_string:

                dotw_month_day, hh_mm_ampm = map(lambda s: s.strip(), start_time_string.split('@'))
                end_hh_mm_ampm = event_html.select_one('.tribe-event-time').string.strip()
                start_time = datetime.combine(event_date, datetime.strptime(hh_mm_ampm, '%I:%M %p').time())
                end_time = datetime.combine(event_date, datetime.strptime(end_hh_mm_ampm, '%I:%M %p').time())

            else:

                dotw_month_day = start_time_string.strip()
                midnight = datetime.combine(event_date, datetime.min.time())
                start_time, end_time = midnight, midnight

            duration_minutes = int((end_time - start_time).total_seconds()) // 60
            start_epoch, end_epoch = map(lambda dt: int(dt.timestamp()), (start_time, end_time))

            category_classes = filter(lambda s: 'category' in s, event_html.attrs['class'])
            categories = sorted([attr.split('-')[-1] for attr in category_classes])

            recurring = event_html.select_one('.event-is-recurring a')
            recurring = recurring.attrs['href'] if recurring else None
            link = event_html.select_one('.summary a').attrs['href']

            common_prefix = 'https://planetgranite.com/sv/event/'
            assert (not link) or link.startswith(common_prefix)
            assert (not recurring) or recurring.startswith(common_prefix)
            recurring, link = map(lambda s: s[len(common_prefix):] if s else False, (recurring, link))

            assert event_date.strftime('%a %B %-d') == dotw_month_day
            assert (duration_from_desc == 0) or (duration_from_desc == duration_minutes)

            events.append((title, instructor, substitutes, cancelled,
                           start_epoch, end_epoch, categories, recurring, link))

    with open('html/events.json', 'w') as json_file_out:
        json.dump(events, json_file_out, indent=4 if debug else None, separators=None if debug else (',', ':'))


if __name__ == '__main__':
    planet_granite_scrape(date.today(), days=15)
