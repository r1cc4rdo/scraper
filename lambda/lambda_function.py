from datetime import date
import subprocess
import sys

from download_to_json import planet_granite_scrape


def execute(cwd, cmdline):
    ret = subprocess.run(cmdline, cwd=cwd, capture_output=True, shell=True, check=False)
    print('\n'.join(('Cwd: ' + cwd, 'Cmd: ' + cmdline, 'Out: ' + ret.stdout.decode(), 'Err: ' + ret.stderr.decode())))


def lambda_handler(event, context):

    url, repository = 'github.com/planetgranite', 'planetgranite.github.io'
    username, token = 'planetgranite', 'fb54a5f5af61054539c4d45e77be26ebf91033bd'

    print(execute('/tmp', f'git clone https://{url}/{repository}.git'))
    planet_granite_scrape(date.today(), days=15, destination=f'/tmp/{repository}/events.json')

    commands = ['export HOME=/tmp',
                f'export PYTHONPATH={";".join(sys.path)}',
                'git config --global user.name "PG Scraper Lambda"',
                'git config --global user.email "lambda@function.aws"',
                f'git commit -am "Uploaded by lambda {date.today()}"',
                f'git push https://{username}:{token}@{url}/{repository}']
    print(execute(f'/tmp/{repository}', ';'.join(commands)))
