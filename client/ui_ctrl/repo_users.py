from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QDialog, QMessageBox

from .errors import show_error
from .list_move import ListMoveController
from .search import ListSearchController
from api.commands.error import (
        InvalidLoginError,
        UserIsAdminError,
        InvalidRepoNameError,
        RepoNotFoundError,
        RepoAllowedError,
        RepoNotAllowedError,
        CommandError,
)
from common import bullet_list, Role
from ui import Ui_RepoUsers

class RepoUsersController:
    class Signals(QObject):
        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(bool)
        def apply(self, _):
            self.control.apply()

        @Slot(bool)
        def reset(self, _):
            self.control.reset()

    def __init__(self,
                 parent: 'QWidget',
                 repo_name: str,
                 user_cmds: 'api.commands.UserPackage',
                 access_cmds: 'api.commands.AccessPackage'):
        self.repo_name = repo_name
        self.user_cmds = user_cmds
        self.access_cmds = access_cmds
        self.signals = self.Signals(self)

        self.dialog = QDialog(parent)
        self.ui = Ui_RepoUsers()
        self.ui.setupUi(self.dialog)

        self.list_move = None
        self.populate_lists()
        self.allowed_search = ListSearchController(
                self.ui.allowed_search_box,
                self.ui.allowed_search_button,
                self.ui.allowed)
        self.ui.denied_search = ListSearchController(
                self.ui.denied_search_box,
                self.ui.denied_search_button,
                self.ui.denied)

        self.ui.apply.clicked.connect(self.signals.apply)
        self.ui.reset.clicked.connect(self.signals.reset)

    def populate_lists(self):
        try:
            allowed = set(self.access_cmds.users(self.repo_name))
        except (InvalidRepoNameError, RepoNotFoundError, CommandError) as ex:
            allowed = set()
            show_error(self.dialog, ex)
        try:
            user_roles = self.user_cmds.list()
        except CommandError as ex:
            user_roles = tuple()
            show_error(self.dialog, ex)

        users = set(self.users_by_role(user_roles, Role.User))
        denied = users - allowed
        # eliminate admins
        allowed.intersection_update(users)

        self.ui.allowed.clear()
        self.ui.allowed.addItems(allowed)
        self.ui.denied.clear()
        self.ui.denied.addItems(denied)

        if self.list_move:
            self.list_move.disconnect()
        self.list_move = ListMoveController(
                self.ui.allowed, self.ui.deny,
                self.ui.denied, self.ui.allow)

    def apply(self):
        to_deny = self.list_move.diff(ListMoveController.Direction.Right)
        to_allow = self.list_move.diff(ListMoveController.Direction.Left)
        msg = []
        if to_deny:
            msg.append(self.dialog.tr('Users to deny:'))
            msg.append(bullet_list(to_deny))
        if to_allow:
            msg.append(self.dialog.tr('Users to allow:'))
            msg.append(bullet_list(to_allow))
        if not msg:
            return

        ok = QMessageBox.question(
                self.dialog,
                self.dialog.tr('Apply user access?'),
                '\n'.join(msg)
        )
        if ok:
            try:
                for user in to_deny:
                    try:
                        self.access_cmds.deny(user, self.repo_name)
                    except (
                            InvalidLoginError,
                            UserIsAdminError,
                            RepoNotAllowedError
                    ) as ex:
                        show_error(self.dialog, ex)

                for user in to_allow:
                    try:
                        self.access_cmds.allow(user, self.repo_name)
                    except (
                            InvalidLoginError,
                            UserIsAdminError,
                            RepoAllowedError
                    ) as ex:
                        show_error(self.dialog, ex)
            except CommandError as ex:
                show_error(self.dialog, ex)

    def reset(self):
       self.populate_lists()

    @staticmethod
    def users_by_role(user_roles: list[tuple[str, str]], role: Role):
        for user, user_role in user_roles:
            if user_role == role.value:
                yield user
