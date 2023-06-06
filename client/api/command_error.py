class CommandError(RuntimeError):
    ''' Exception that is thrown when SSH command is failed '''
    ERR_MSG = 'Unknown error'

    def __init__(self, *args, **kw):
        msg = ''.join((
            self.ERR_MSG, ': ',
            ', '.join((
                *args,
                *map(self.pair_msg, kw.items())
            ))
        ))
        super.__init__(msg)

    @staticmethod
    def pair_msg(pair):
        return '='.join(map(str, pair))

# Login errors
class LoginError(CommandError):
    ERR_MSG = 'Unknown login error'
    def __init__(self, login):
        super.__init__(login=login)
        self.login = login

class InvalidLoginError(LoginError):
    ERR_MSG = 'Invalid login'

class UserNotFoundError(LoginError):
    ERR_MSG = 'User does not exist'

class UserExistsError(LoginError):
    ERR_MSG = 'User exists'

class UserNotAdminError(LoginError):
    ERR_MSG = 'Not an admin'

class UserIsAdminError(LoginError):
    ERR_MSG = 'Is admin'

# Repo errors
class RepoError(CommandError):
    ERR_MSG = 'Unknown repo error'
    def __init__(self, repo):
        super.__init__(repo=repo)
        self.repo = repo

class InvalidRepoNameError(RepoError):
    ERR_MSG = 'Invalid repo name'

class RepoNotFoundError(RepoError):
    ERR_MSG = 'Repo does not exits'

class RepoExistsError(RepoError):
    ERR_MSG = 'Repo exists'

# Access errors
class AccessError(CommandError):
    ERR_MSG = 'Unknown access error'
    def __init__(self, login, repo):
        super.__init__(login=login, repo=repo)
        self.login = login
        self.repo = repo

class RepoAllowedError(CommandError):
    ERR_MSG = 'Repo is allowed'

class RepoNotAllowedError(CommandError):
    ESS_MSG = 'Repo is not allowed'

SPECIFIC = [
    InvalidLoginError,
    UserNotFoundError,
    UserExistsError,
    UserNotAdminError,
    UserIsAdminError,
    InvalidRepoNameError,
    RepoNotFoundError,
    RepoExistsError
]
SPECIFIC_MAP = {
        ex.ERR_MSG: ex
        for ex in SPECIFIC
}

__all__ = ['CommandError', *map(lambda ex: ex.__name__, SPECIFIC), 'SPECIFIC_MAP']
