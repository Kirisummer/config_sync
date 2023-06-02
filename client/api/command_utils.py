from inspect import getmembers, ismethod
from dataclasses import dataclass
from functools import wraps

@dataclass(frozen=True)
class Package:
    ''' Class that represents command package '''
    ssh: 'SSH'
    pkg_name: str

    def __post_init__(self):
        ''' Set package name for every method decorated with
            decorators below. Names are set for underlying methods.
        '''
        for _, func in getmembers(self, ismethod):
            if hasattr(func, '_pkg_decorated'):
                # there's only one closure
                func.__closure__[0].cell_contents._pkg_name = self.pkg_name

    def _ssh(self, command: str, *args: tuple[str]):
        return self.ssh.run(self.pkg_name, command, *args)

class CommandError(RuntimeError):
    ''' Exception that is thrown when SSH command is failed '''
    pass

def handle_fail(method, *args, **kw):
    ''' Handle possible failure or return call result '''
    res = method(*args, **kw)
    if not res.returncode:
        return res
    if hasattr(method, '_pkg_name'):
        cmd_name = f'`{method._pkg_name} {method.__name__}`'
    else:
        cmd_name = f'`{method.__name__}`'
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
