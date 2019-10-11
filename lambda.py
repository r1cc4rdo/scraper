import json
from datetime import date, timedelta

from botocore.vendored import requests  # deprecated, need to install a zip package (for bs4 too, and github)
# https://github.com/lambci/git-lambda-layer
# https://stackoverflow.com/questions/34629574/can-bash-script-be-written-inside-a-aws-lambda-function
# https://docs.python.org/2/library/subprocess.html
# refresh 1 mo every 15 days https://github.com/mixu/markdown-styles-lambda https://github.com/mixu/ghost-render https://github.com/mixu/markdown-styles
# https://medium.com/@kagemusha_/scraping-on-a-schedule-with-aws-lambda-and-cloudwatch-caf65bc38848
# save log

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


def lambda_handler(event, context):
    urls = list(calendar_urls(date.today(), days=30))
    page = requests.get(urls[0]).content.decode()

    return {
        'statusCode': 200,
        'body': json.dumps(page)
    }
