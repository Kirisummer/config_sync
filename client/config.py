from logging import getLogger
from copy import deepcopy
from dataclasses import dataclass, field
from functools import wraps
from itertools import starmap
from typing import ClassVar, TypedDict

from api.ssh import SSHCreds
from common import Repo

import tomlkit
from PySide6.QtCore import QReadWriteLock

LOGGER = getLogger(__file__)

UserConfig = TypedDict('UserConfig', {'login': str, 'host': str, 'port': int})
RepoConfig = dict[str, str]
Config = TypedDict('Config', {'user': UserConfig, 'repos': RepoConfig})

@dataclass(frozen=True)
class ConfigManager:
    DEFAULT_CONFIG: ClassVar[Config] = {'repos': {}}

    config_path: 'Path'
    config_lock: QReadWriteLock = field(default_factory=QReadWriteLock)

    @staticmethod
    def read_lock(method):
        @wraps(method)
        def inner(self, *argv, **kw):
            self.config_lock.lockForRead()
            try:
                return method(self, *argv, **kw)
            finally:
                self.config_lock.unlock()
        return inner

    @staticmethod
    def write_lock(method):
        @wraps(method)
        def inner(self, *argv, **kw):
            self.config_lock.lockForWrite()
            try:
                return method(self, *argv, **kw)
            finally:
                self.config_lock.unlock()
        return inner

    def _load(self):
        try:
            with open(self.config_path) as file:
                return tomlkit.load(file)
        except OSError:
            LOGGER.warning('Failed to read config: %s', self.config_path)
            config = deepcopy(ConfigManager.DEFAULT_CONFIG)
            self._save(config)
            return config

    def _save(self, config: Config):
        try:
            with open(self.config_path, 'w') as file:
                return tomlkit.dump(config, file)
        except OSError:
            LOGGER.warning('Failed to write to config: %s', self.config_path)


    @read_lock
    def get_last_creds(self) -> SSHCreds:
        ''' Returns SSHCreds from config without password '''
        config = self._load().get('user', {})
        return SSHCreds(
                config.get('login', None),
                None,
                config.get('host', None),
                config.get('port', None)
        )

    @write_lock
    def save_creds(self, creds: SSHCreds):
        ''' Save creds without password '''
        config = self._load()
        config['user'] = {
                'login': creds.login,
                'host': creds.host,
                'port': creds.port
        }
        self._save(config)

    @read_lock
    def get_repos(self) -> list[Repo]:
        config = self._load()['repos']
        return list(starmap(Repo, config.items()))

    @write_lock
    def add_repo(self, repo: Repo):
        config = self._load()
        config['repos'][repo.name] = str(repo.path)
        self._save(config)
    
    @write_lock
    def delete_repos(self, repo_names: list[str]):
        config = self._load()
        repos = config['repos']
        for repo_name in repo_names:
            if repo_name in repos:
                del repos[repo_name]
        self._save(config)
