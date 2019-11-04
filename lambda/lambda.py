from datetime import date
import subprocess
import sys


def execute(cwd, cmdline):
    ret = subprocess.run(cmdline, cwd=cwd, capture_output=True, shell=True, check=False)
    print('\n'.join(('Cwd: ' + cwd, 'Cmd: ' + cmdline, 'Out: ' + ret.stdout.decode(), 'Err: ' + ret.stderr.decode())))


def lambda_handler(event, context):

    repository = 'github.com/r1cc4rdo/scraper.git'
    username, token = 'r1cc4rdo', '<<<access token id>>>'

    print(execute('/tmp', f'git clone https://{repository}'))

    commands = ['export HOME=/tmp',
                f'export PYTHONPATH={";".join(sys.path)}',
                'git config --global user.name "PG Scraper Lambda"',
                'git config --global user.email "lambda@function.aws"',
                f'{sys.executable} download_to_json.py',
                f'git commit -am "Uploaded by lambda {date.today()}"',
                f'git push https://{username}:{token}@{repository}']
    print(execute('/tmp/scraper', ';'.join(commands)))
