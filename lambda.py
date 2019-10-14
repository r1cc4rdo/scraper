import subprocess
from datetime import date, timedelta
from collections import defaultdict
from multiprocessing.pool import ThreadPool as Pool

from bs4 import BeautifulSoup
import requests


def exec(cwd, cmdline):
    print(f'Directory: {cwd}')
    print(f'Command: {cmdline}')
    opts = {'cwd': cwd, 'capture_output': True, 'shell': True, 'check': False}
    ret = subprocess.run(cmdline, **opts)
    print(f'Returned: {ret}')
    return ret.stdout.decode()


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
    start_time = time.process_time()
    pages = Pool(8).map(download, calendar_urls(starting_date, days))
    print(f'\nElapsed time: {time.process_time() - start_time:.2f}')

    start_time = time.process_time()
    events = defaultdict(list)
    with open('/tmp/scraper/event_by_date.md', 'w') as markdown_out:
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
                categories = sorted(
                    [attr.split('-')[-1] for attr in filter(lambda s: 'category' in s, event.attrs['class'])])
                recurring = event.select_one('.event-is-recurring a')
                recurring = recurring.attrs['href'] if recurring else None
                link = event.select_one('.summary a').attrs['href']

                bold = "" if recurring else "**"
                markdown_out.write(f'1. [{bold}{start} -- {end} {desc}{bold}]({link})\n')
                events[title.lower()].append((title, categories, start, end, specs, recurring, link))

        markdown_out.write(f'---\n*Last updated: {date.today()}*\n')
    print(f'\nElapsed time: {time.process_time() - start_time:.2f}')

    start_time = time.process_time()
    with open('/tmp/scraper/event_by_type.md', 'w') as markdown_out:
        for desc in sorted(events, key=lambda d: ('events' not in events[d][0][1], events[d][0][1], events[d][0][0])):

            markdown_out.write(f'## {events[desc][0][0]} ({" ".join(events[desc][0][1])})\n')
            for title, categories, start, end, specs, recurring, link in events[desc]:
                link_text = f'{start} -- {end} {specs}'
                bold = "" if recurring else "**"
                markdown_out.write(f'1. [{bold}{link_text.strip()}{bold}]({link})\n')

        markdown_out.write(f'---\n*Last updated: {date.today()}*\n')
    print(f'\nElapsed time: {time.process_time() - start_time:.2f}')


def lambda_handler(event, context):
    print(exec('/tmp', 'git clone  https://github.com/r1cc4rdo/scraper.git'))

    print(exec('/tmp/scraper', 'echo $(date) > event_by_date.md'))

    username = 'r1cc4rdo'
    password = 'origamicio123'
    commands = ['export HOME=/tmp',
                'git config --global user.name "Lambda"',
                'git config --global user.email "lambda@function.aws"',
                f'git commit -am "Uploaded by lambda {date.today()}"',
                f'git push https://{username}:{password}@github.com/r1cc4rdo/scraper.git']
    print(exec('/tmp/scraper', ';'.join(commands)))




# pycharm integration
# parallel execution
# static website?
# password authentication
# filter: tags, dates, times, search term

# https://github.com/lambci/git-lambda-layer
# https://stackoverflow.com/questions/34629574/can-bash-script-be-written-inside-a-aws-lambda-function
# https://docs.python.org/2/library/subprocess.html
# refresh 1 mo every 15 days https://github.com/mixu/markdown-styles-lambda https://github.com/mixu/ghost-render https://github.com/mixu/markdown-styles
# https://medium.com/@kagemusha_/scraping-on-a-schedule-with-aws-lambda-and-cloudwatch-caf65bc38848
# save log



import time
from multiprocessing import Process, Pipe
import boto3


class VolumesParallel(object):
    """Finds total volume size for all EC2 instances"""

    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def instance_volumes(self, instance, conn):
        """
        Finds total size of the EBS volumes attached
        to an EC2 instance
        """
        instance_total = 0
        for volume in instance.volumes.all():
            instance_total += volume.size
        conn.send([instance_total])
        conn.close()

    def total_size(self):
        """
        Lists all EC2 instances in the default region
        and sums result of instance_volumes
        """
        print
        "Running in parallel"

        # get all EC2 instances
        instances = self.ec2.instances.all()

        # create a list to keep all processes
        processes = []

        # create a list to keep connections
        parent_connections = []

        # create a process per instance
        for instance in instances:
            # create a pipe for communication
            parent_conn, child_conn = Pipe()
            parent_connections.append(parent_conn)

            # create the process, pass instance and connection
            process = Process(target=self.instance_volumes, args=(instance, child_conn,))
            processes.append(process)

        # start all processes
        for process in processes:
            process.start()

        # make sure that all processes have finished
        for process in processes:
            process.join()

        instances_total = 0
        for parent_connection in parent_connections:
            instances_total += parent_connection.recv()[0]

        return instances_total


def lambda_handler(event, context):
    volumes = VolumesParallel()
    _start = time.time()
    total = volumes.total_size()
    print
    "Total volume size: %s GB" % total
    print
    "Sequential execution time: %s seconds" % (time.time() - _start)


Performance