from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QMessageBox, QInputDialog, QLineEdit

from .create_user import CreateUserController
from .errors import show_error
from api.command_error import (
        InvalidLoginError, 
        UserExistsError, 
        UserNotFoundError,
        UserIsAdminError,
        CommandError,
)
from common import Role

class UserControllerBase:
    class Signals(QObject):
        users_updated = Signal()

        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(str, str)
        def create_user(self, login, passwd):
            self.control.create_user(login, passwd)

    def __init__(self, dialog: 'QDialog', user_cmds: 'api.commands.UserPackage'):
        self.dialog = dialog
        self.user_cmds = user_cmds
        self.signals = self.Signals(self)

    def replace_ssh(self, user_cmds: 'api.commands.UserPackage'):
        self.user_cmds = user_cmds

    @staticmethod
    def get_selected_user(list_widget: 'QListWidget'):
        return list_widget.selectedItems()[0].text()

    def populate_users(self, user_list: 'QListWidget', admin_list: 'QListWidget' = None):
        user_list.clear()
        if admin_list:
            admin_list.clear()

        for user, role in self.user_cmds.list():
            match Role(role):
                case Role.User:
                    user_list.addItem(user)
                case Role.Admin:
                    if admin_list:
                        admin_list.addItem(user)

    def create_user_dialog(self):
        dialog = CreateUserController(self.dialog)
        dialog.signals.creds_entered.connect(self.signals.create_user)
        dialog.dialog.exec()

    def create_user(self, login: str, passwd: str):
        try:
            self.user_cmds.create(login, passwd)
        except (InvalidLoginError, UserExistsError, CommandError) as ex:
            show_error(self.dialog, ex)
        else:
            self.signals.users_updated.emit()

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
            else:
                self.signals.users_updated.emit()

    def change_password_dialog(self, login: str):
        passwd, ok = QInputDialog.getText(
                self.dialog,
                self.dialog.tr('Password change'),
                ' '.join((self.dialog.tr('New password for'), login)),
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
