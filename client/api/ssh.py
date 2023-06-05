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
class SSHCmdBits:
    passwd_pipe: tuple[str]
    ssh_opts: tuple[str]
    port_arg: str

    @classmethod
    def get(cls):
        match system():
            case 'Linux':
                return cls.get_linux_ssh_cmd()
            case 'Windows':
                return cls.get_win_ssh_cmd()
            case os_name:
                raise NotImplementedError(f'OS not supported: {os_name}')

    @staticmethod
    def get_linux_ssh_cmd():
        return SSHCmdBits(
                ('sshpass', '-p'),
                ('ssh', '-q', '-o', 'StrictHostKeyChecking=no', \
                              '-o', 'UserKnownHostsFile=/dev/null'),
                '-p'
        )

    @staticmethod
    def get_win_ssh_cmd():
        return SSHCmdBits(
                ('plink', '-pw'),
                ('-ssh',),
                '-p'
        )

@dataclass(frozen=True)
class SSH:
    cmd_bits: SSHCmdBits
    creds: SSHCreds

    def run(self, *command, input: bytes=None):
        command = (
                *self.cmd_bits.passwd_pipe, self.creds.password,
                *self.cmd_bits.ssh_opts,
                self.cmd_bits.port_arg, str(self.creds.port),
                f'{self.creds.login}@{self.creds.host}', *command
        )
        return run(command, capture_output=True, input=input)

    @classmethod
    def get(cls, creds: SSHCreds):
        return cls(SSHCmdBits.get(), creds)
