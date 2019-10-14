import sys
import subprocess
from datetime import date


def exec(cwd, cmdline):
    opts = {'cwd': cwd, 'capture_output': True, 'shell': True, 'check': False}
    return subprocess.run(cmdline, **opts).stdout.decode()


def lambda_handler(event, context):

    repository = 'github.com/r1cc4rdo/scraper.git'
    username, token = 'r1cc4rdo', '<<<access token id>>>'

    exec('/tmp', f'git clone https://{repository}')

    sys.path.append('/tmp/scraper')
    from lambda import planet_granite_scrape
    planet_granite_scrape(date.today(), 15)

    commands = ['export HOME=/tmp',
                'git config --global user.name "PG Scraper Lambda"',
                'git config --global user.email "lambda@function.aws"',
              f'git commit -am "Uploaded by lambda {date.today()}"',
              f'git push https://{username}:{token}@{repository}']
    exec('/tmp/scraper', ';'.join(commands))
