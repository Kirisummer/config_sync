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

class UserNotFound(LoginError):
    ERR_MSG = 'User does not exist'

class UserExists(LoginError):
    ERR_MSG = 'User exists'

class UserNotAdmin(LoginError):
    ERR_MSG = 'Not an admin'

class UserIsAdmin(LoginError):
    ERR_MSG = 'Is admin'

# Repo errors
class RepoError(CommandError):
    ERR_MSG = 'Unknown repo error'
    def __init__(self, repo):
        super.__init__(repo=repo)
        self.repo = repo

class InvalidRepoName(RepoError):
    ERR_MSG = 'Invalid repo name'

class RepoNotFound(RepoError):
    ERR_MSG = 'Repo does not exits'

class RepoExists(RepoError):
    ERR_MSG = 'Repo exists'

# Access errors
class AccessError(CommandError):
    ERR_MSG = 'Unknown access error'
    def __init__(self, login, repo):
        super.__init__(login=login, repo=repo)
        self.login = login
        self.repo = repo

class RepoAllowed(CommandError):
    ERR_MSG = 'Repo is allowed'

class RepoNotAllowed(CommandError):
    ESS_MSG = 'Repo is not allowed'

SPECIFIC = [
    InvalidLoginError,
    UserNotFound,
    UserExists,
    UserNotAdmin,
    UserIsAdmin,
    InvalidRepoName,
    RepoNotFound,
    RepoExists
]
SPECIFIC_MAP = {
        ex.ERR_MSG: ex
        for ex in SPECIFIC
}

__all__ = ['CommandError', *map(lambda ex: ex.__name__, SPECIFIC), 'SPECIFIC_MAP']
