from datetime import date
import subprocess
import sys


def exec(cwd, cmdline):
    opts = {'cwd': cwd, 'capture_output': True, 'shell': True, 'check': False}
    ret = subprocess.run(cmdline, **opts)
    print('\n'.join((cwd, cmdline, ret.stdout.decode(), ret.stderr.decode())))


def lambda_handler(event, context):
    repository = 'github.com/r1cc4rdo/scraper.git'
    username, token = 'r1cc4rdo', '<<<access token id>>>'

    print(exec('/tmp', f'git clone https://{repository}'))

    commands = ['export HOME=/tmp',
                f'export PYTHONPATH={";".join(sys.path)}',
                'git config --global user.name "PG Scraper Lambda"',
                'git config --global user.email "lambda@function.aws"',
                f'{sys.executable} download_to_json.py',
                f'git commit -am "Uploaded by lambda {date.today()}"',
                f'git push https://{username}:{token}@{repository}']
    print(exec('/tmp/scraper', ';'.join(commands)))
