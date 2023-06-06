from PySide6.QtWidgets import QDialog
from PySide6.QtCore import QObject, Slot

from ui import Ui_UsersAdmin

from .user_base import UserControllerBase

class AdminUserController(UserControllerBase):
    class AdminSignals(QObject):
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
        def populate_users(self,):
            self.control.populate_users(self.control.ui.users)

        @Slot()
        def update_user_buttons(self):
            self.control.update_user_buttons()

    def __init__(self, user_cmds: 'api.commands.UserPackage'):
        super().__init__(QDialog(), user_cmds)
        self.ui = Ui_UsersAdmin()
        self.ui.setupUi(self.dialog)
        self.admin_signals = self.AdminSignals(self)

        self.populate_users(self.ui.users)

        self.ui.create.clicked.connect(self.admin_signals.create_user_dialog)
        self.ui.delete_.clicked.connect(self.admin_signals.delete_user_dialog)
        self.ui.passwd.clicked.connect(self.admin_signals.change_password_dialog)
        self.ui.accept.accepted.connect(self.dialog.accept)

        self.signals.users_updated.connect(self.admin_signals.populate_users)

        self.update_user_buttons()
        self.ui.users.itemSelectionChanged.connect(self.admin_signals.update_user_buttons)

    def update_user_buttons(self):
        users_selection = self.ui.users.selectedItems()
        self.ui.delete_.setEnabled(bool(users_selection))
        self.ui.passwd.setEnabled(bool(users_selection))
