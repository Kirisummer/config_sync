from PySide6.QtWidgets import QDialog, QMessageBox
from PySide6.QtCore import QObject, Slot

from .errors import show_error
from .list_move import ListMoveController
from .user_base import UserControllerBase
from api.command_error import (
        InvalidLoginError, 
        UserExistsError, 
        UserNotFoundError,
        UserIsAdminError,
        UserNotAdminError,
        CommandError,
)
from common import bullet_list
from ui import Ui_UsersOwner

class OwnerUserController(UserControllerBase):
    class OwnerSignals(QObject):
        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(bool)
        def create_user_dialog(self, _):
            self.control.create_user_dialog()

        @Slot(bool)
        def delete_user_dialog(self, _):
            user = self.control.get_selected_user(self.control.ui.users)
            self.control.delete_user_dialog(user)

        @Slot(bool)
        def change_password_dialog(self, _):
            user = self.control.get_selected_user(self.control.ui.users)
            self.control.change_password_dialog(user)

        @Slot(bool)
        def apply(self, _):
            self.control.apply()

        @Slot(bool)
        def discard(self, _):
            self.control.discard()

        @Slot()
        def populate_users(self):
            self.control.populate_users()

        @Slot()
        def update_user_buttons(self):
            self.control.update_user_buttons()

    def __init__(self,
                 parent: 'QWidget',
                 user_cmds: 'api.commands.UserPackage',
                 admin_cmds: 'api.commands.AdminPackage'):
        super().__init__(QDialog(parent), user_cmds)
        self.admin_cmds = admin_cmds

        self.ui = Ui_UsersOwner()
        self.ui.setupUi(self.dialog)
        self.owner_signals = self.OwnerSignals(self)

        self.list_move = None
        self.populate_users()
        
        self.ui.create.clicked.connect(self.owner_signals.create_user_dialog)
        self.ui.delete_.clicked.connect(self.owner_signals.delete_user_dialog)
        self.ui.passwd.clicked.connect(self.owner_signals.change_password_dialog)
        self.ui.apply.clicked.connect(self.owner_signals.apply)
        self.ui.reset.clicked.connect(self.owner_signals.discard)

        self.signals.users_updated.connect(self.owner_signals.populate_users)

        # handle list selection -> delete, passwd buttons enable
        self.update_user_buttons()
        self.ui.users.itemSelectionChanged.connect(self.owner_signals.update_user_buttons)

    def populate_users(self):
        try:
            super().populate_users(self.ui.users, self.ui.admins)
        except CommandError as ex:
            show_error(self.dialog, ex)
        else:
            if self.list_move:
                self.list_move.disconnect()
            self.list_move = ListMoveController(
                    self.ui.users, self.ui.to_admins,
                    self.ui.admins, self.ui.to_users,
            )
    
    def apply(self):
        to_promote = self.list_move.diff(ListMoveController.Direction.Right)
        to_demote = self.list_move.diff(ListMoveController.Direction.Left)

        msg = []
        if to_promote:
            msg.append(self.dialog.tr('Users to promote:'))
            msg.append(bullet_list(to_promote))
        if to_demote:
            msg.append(self.dialog.tr('Admins to demote:'))
            msg.append(bullet_list(to_demote))

        ok = QMessageBox.question(
                self.dialog,
                self.dialog.tr('Promotion/Demotion'),
                '\n'.join(msg)
        )
        if ok:
            for user in to_promote:
                try:
                    self.admin_cmds.promote(user)
                except (UserNotFoundError, UserIsAdminError, CommandError) as ex:
                    show_error(self.dialog, ex)
            for user in to_demote:
                try:
                    self.admin_cmds.demote(user)
                except (UserNotFoundError, UserNotAdminError, CommandError) as ex:
                    show_error(self.dialog, ex)
        self.populate_users()

    def update_user_buttons(self):
        users_selection = self.ui.users.selectedItems()
        self.ui.delete_.setEnabled(bool(users_selection))
        self.ui.passwd.setEnabled(bool(users_selection))
