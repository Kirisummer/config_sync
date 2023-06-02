from dataclasses import dataclass
from platform import system
from subprocess import run

@dataclass(frozen=True)
class SSHCreds:
    login: str
    password: str
    host: str
    port: int

@dataclass(frozen=True)
class SSH:
    ssh_cmd: tuple[str]

    def run(self, *command):
        return run(
                (*self.ssh_cmd, *command),
                capture_output=True,
        )

    @classmethod
    def get(cls, ssh_creds):
        match system():
            case 'Linux':
                return LinuxSSH(ssh_creds)
            case 'Windows':
                return WinSSH(ssh_creds)
            case os_name:
                raise NotImplementedError(f'OS not supported: {os_name}')

class LinuxSSH(SSH):
    def __init__(self, ssh_creds):
        super().__init__((
                *get_linux_ssh_cmd(ssh_creds.password),
                '-p', str(ssh_creds.port),
                f'{ssh_creds.login}@{ssh_creds.host}'
        ))

class WinSSH(SSH):
    def __init__(self, ssh_creds):
        super().__init__((
                *get_win_ssh_cmd(ssh_creds.password),
                '-P', str(ssh_creds.port),
                f'{ssh_creds.login}@{ssh_creds.host}'
        ))

def get_linux_ssh_cmd(password):
    return 'sshpass', '-p', password, \
           'ssh', '-q', '-o', 'StrictHostKeyChecking=no', \
                        '-o', 'UserKnownHostsFile=/dev/null'

def get_win_ssh_cmd(password):
    return 'plink', '-ssh', '-pw', password

def get_ssh_cmd(password):
    match system():
        case 'Linux':
            return get_linux_ssh_cmd(password)
        case 'Windows':
            return get_win_ssh_cmd(password)
        case os_name:
            raise NotImplementedError(f'OS not supported: {os_name}')
