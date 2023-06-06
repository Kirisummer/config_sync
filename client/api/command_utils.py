from inspect import getmembers, ismethod
from dataclasses import dataclass
from functools import wraps
import re

from .command_error import *

@dataclass(frozen=True)
class Package:
    ''' Class that represents command package '''
    ssh: 'SSH'
    pkg_name: str

    def _ssh(self, command: str, *args: tuple[str]):
        return self.ssh.run(self.pkg_name, command, *args)

def handle_fail(method, *args, **kw):
    ''' Handle possible failure or return call result '''
    res = method(*args, **kw)
    if not res.returncode:
        return res
    parse_and_raise(res)
    raise CommandError(f'{cmd_name} failed', res.stderr, *args, **kw)

def action(method):
    ''' Check that call via SSH was successful '''
    @wraps(method)
    def inner(*args, **kw):
        handle_fail(method, *args, **kw)
    inner._pkg_decorated = True
    return inner

def decode_bytes(b: bytes) -> str:
    return b.decode('utf-8')

def value_request(method):
    ''' Parse successful call's result to a single value '''
    @wraps(method)
    def inner(*args, **kw):
        res = handle_fail(method, *args, **kw)
        return decode_bytes(res.stdout.strip())
    inner._pkg_decorated = True
    return inner

def list_request(method):
    ''' Parse successful call's result to a list of values '''
    @wraps(method)
    def inner(*args, **kw):
        res = handle_fail(method, *args, **kw)
        return list(map(decode_bytes, res.stdout.strip().split()))
    inner._pkg_decorated = True
    return inner

def table_request(method):
    ''' Parse successful call's result to a table of values '''
    @wraps(method)
    def inner(*args, **kw):
        res = handle_fail(method, *args, **kw)
        return [
                list(map(decode_bytes, line.split()))
                for line in res.stdout.strip().split(b'\n')
        ]
    inner._pkg_decorated = True
    return inner

def parse_and_raise(res: 'CompletedProcess'):
    ''' Try to parse specific exception, fallback to CommandError(stderr) '''
    stderr = res.stderr.decode('utf-8')
    try:
        # error caught by validator
        cmd, msg, args = stderr.split(': ', 2)
        ex_type = SPECIFIC_MAP.get(msg, None)
        args = parse_args(args)
    except ValueError:
        ex_type, args = CommandError, (stderr,)
    raise ex_type(**args)

def parse_args(arg_string: str):
    ''' Parse exception arguments '''
    breakpoint()
    def parse_pair(pair_str):
        name, value = re.match(r'(\w+)=`(.+)`', pair_str).groups()
        return name, value
    return {
            name: value
            for name, value in map(parse_pair, arg_string.split(' '))
    }
