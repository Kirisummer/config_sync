from api.command_errors import (
    InvalidLoginError,
    UserNotFoundError,
    UserExistsError,
    UserNotAdminError,
    UserIsAdminError,
    InvalidRepoNameError,
    RepoNotFoundError,
    RepoExistsError
)

def show_error(widget: 'QWidget', ex: CommandError):
    title = widget.tr(ex.ERR_MSG)
    if type(ex) in ERROR_TABLE:
        label = widget.tr(ERROR_TABLE[ex]).format(*args[1:])
    else:
        label = ex.message
    QMessageBox.critical(widget, title, label)

ERROR_TABLE = {
        InvalidLoginError:    'Login is not valid. Login may consist of ' \
                              'latin letters, numbers and characters "._-"',
        UserNotFoundError:    'User {} was not found on the server',
        UserExistsError:      'User {} already exists on the server',
        UserNotAdminError:    'User {} is not an admin',
        UserIsAdminError:     'User {} is already an admin',
        InvalidRepoNameError: 'Repository name {} is not valid. ' \
                              'Repository name may consist of letters, ' \
                              'numbers, spaces and symbols "_.-"',
        RepoNotFoundError:    'Repository {} was not found on the server',
        RepoExistsError:      'Repository {} already exists on the server',
        RepoAllowedError:     'User {} already has an access to {}',
        RepoNotAllowedError:  'User {} does not have an access to {}',
}
