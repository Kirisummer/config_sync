from .errors import show_error
from api.command_errors import (
        InvalidLoginError, 
        UserExistsError, 
        UserNotFoundError,
        UserIsAdminError,
)

class UserControllerBase:
    def __init__(self, dialog: 'QDialog', user_cmds: 'api.commands.UserPackage'):
        self.dialog = dialog
        self.user_cmds = user_cmds

    def create_user_dialog(self):
        dialog = CreateUserController(self.dialog)
        dialog.signals.creds_entered.connect(
                lambda login, passwd: self.create_user(login, passwd))
        dialog.exec()

    def create_user(self, login: str, passwd: str):
        try:
            self.user_cmds.create(login, passwd)
        except (InvalidLoginError, UserExistsError, CommandError) as ex:
            show_error(self.dialog, ex)

    def delete_user_dialog(self, login: str):
        ok = QMessageBox.question(
                self.dialog,
                self.dialog.tr('Delete user?'),
                self.dialog.tr('Delete user {}?').format(login)
        )
        if ok == QMessageBox.StandardButton.Yes:
            try:
                self.user_cmds.delete(login)
            except (
                    InvalidLoginError,
                    UserNotFoundError,
                    UserIsAdminError,
                    CommandError
            ) as ex:
                show_error(self.dialog, ex)

    def change_password_dialog(self, login: str):
        passwd, ok = QInputDialog.getText(
                self.dialog,
                self.dialog.tr('Password change'),
                ' '.join((self.widget.tr('New password for'), login)),
                QLineEdit.EchoMode.Password
        )
        if ok:
            if passwd:
                try:
                    self.user_cmds.passwd(login, passwd)
                except (InvalidLoginError, UserIsAdminError, CommandError) as ex:
                    show_error(self.dialog, ex)
                else:
                    QMessageBox.information(
                            self.dialog,
                            self.dialog.tr('Success'),
                            self.dialog.tr('Password for {} was changed succesfully').format(login)
                    )
