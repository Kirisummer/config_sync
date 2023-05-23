#!/usr/bin/python3

import signal
from shutil import copyfile
from os import environ
from subprocess import run

passwd_files = 'passwd', 'shadow', 'group', 'gshadow', 'subgid', 'subuid'
passwd_dir = environ['PASSWD_DIR']

def backup_passwd():
    print('Trap activated')
    for file in passwd_files:
        copyfile(f'/etc/{file}', passwd_dir)

signal.signal(signal.SIGINT, backup_passwd)
run(('echo', 'Trap set'))

for file in passwd_files:
    try:
        copyfile(f'{passwd_dir}/{file}', '/etc')
    except Exception as e:
        run(('echo', str(e), *map(str, e.args)))

run(('service', 'ssh', 'start'))

while True:
    pass
