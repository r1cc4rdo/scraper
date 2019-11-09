from datetime import date
import subprocess
import sys

from download_to_json import planet_granite_scrape


def execute(cwd, cmdline):
    ret = subprocess.run(cmdline, cwd=cwd, capture_output=True, shell=True, check=False)
    print(f'\n\nCwd: {cwd}\nCmd: {cmdline}\nOut: {ret.stdout.decode()}\nErr: {ret.stderr.decode()}')


def lambda_handler(event, context):

    url, repository = 'github.com/planetgranite', 'planetgranite.github.io'
    username, token = 'planetgranite', 'f78625eb7d6af25d2d3ee30b1e4da54959a75cc9'

    execute('/tmp', f'git clone https://{url}/{repository}.git')
    planet_granite_scrape(date.today(), days=15, destination=f'/tmp/{repository}/events.json')

    commands = ['export HOME=/tmp',
                f'export PYTHONPATH={":".join(sys.path)}',
                'git config --global user.name "PG Scraper Lambda"',
                'git config --global user.email "lambda@function.aws"',
                f'git commit -am "Uploaded by lambda {date.today()}"',
                f'git push https://{username}:{token}@{url}/{repository}']
    execute(f'/tmp/{repository}', ';'.join(commands))
