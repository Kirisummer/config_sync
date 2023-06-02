from command_utils import (
        action, value_request, list_request, table_request, Package
)

class AccessPackage(Package):
    def __init__(self, ssh: 'SSH'):
        super().__init__(ssh, 'access')

    @action
    def allow(self, login: str, repo: str):
        return self._ssh('allow', login, repo)

    @action
    def deny(self, login: str, repo: str):
        return self._ssh('deny', login, repo)

    @list_request
    def list(self, login: str):
        return self._ssh('list', login)

class AdminPackage(Package):
    def __init__(self, ssh: 'SSH'):
        super().__init__(ssh, 'admin')

    @action
    def promote(self, login: str):
        return self._ssh('promote', login)

    @action
    def demote(self, login: str):
        return self._ssh('demote', login)

class RepoPackage(Package):
    def __init__(self, ssh: 'SSH'):
        super().__init__(ssh, 'repo')

    @action
    def create(self, repo: str):
        return self._ssh('create', repo)

    @action
    def delete(self, repo: str):
        return self._ssh('delete', repo)

    @list_request
    def list(self):
        return self._ssh('list')

class SelfPackage(Package):
    def __init__(self, ssh: 'SSH'):
        super().__init__(ssh, 'self')

    @action
    def passwd(self, password: str):
        return self._ssh('passwd', password)

    @list_request
    def repos(self):
        return self._ssh('repos')

class UserPackage(Package):
    def __init__(self, ssh: 'SSH'):
        super().__init__(ssh, 'user')

    @action
    def create(self, login: str, password: str):
        return self._ssh('create', login, password)

    @action
    def delete(self, login: str):
        return self._ssh('delete', login)

    @table_request
    def list(self):
        return self._ssh('list')

    @action
    def passwd(self, login: str, password: str):
        return self._ssh('passwd', login, password)

