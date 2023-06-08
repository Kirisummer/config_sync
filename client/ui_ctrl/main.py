from PySide6.QtCore import QObject, Slot, Signal
from PySide6.QtWidgets import QInputDialog, QMessageBox, QLineEdit

from .config import RepoConfigController
from .repo import RepoPageController
from .user_admin import AdminUserController
from .user_owner import OwnerUserController
from .repo_users import RepoUsersController

from api.commands.packages import (
        AdminPackage, AccessPackage, RepoPackage, SelfPackage, UserPackage
)
from api.commands.error import InvalidPasswordError, CommandError
from api.ssh import SSH
from api.git import GitRepo, GitCloner
from common import Role
from ui import Ui_MainWindow

class MainController:
    class Signals(QObject):
        logged_out = Signal()

        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot()
        def populate_tabs(self):
            self.control.populate_tabs()

        @Slot(int)
        def discard(self, tab_idx):
            self.control.config_tab.discard()

        @Slot(bool)
        def open_users(self, checked):
            self.control.open_users()

        @Slot(bool)
        def open_repo_users(self, checked):
            self.control.open_repo_users()

        @Slot(int)
        def check_enable_repo_menu(self, row):
            self.control.check_enable_repo_menu(row)

        @Slot()
        def fetch(self):
            self.control.fetch()

        @Slot()
        def push(self):
            self.control.push()

        @Slot()
        def change_passwd(self):
            self.control.change_passwd()

    CONFIG_TAB = 'Repository management'

    def __init__(self,
                 role: Role,
                 config: 'config.ConfigManager',
                 creds: 'api.ssh.SSHCreds'):
        self.role = role
        self.config = config
        self.creds = creds
        self.signals = self.Signals(self)

        ssh = SSH.get(creds)
        self.config_tab = RepoConfigController(
                self.config,
                RepoPackage(ssh),
                SelfPackage(ssh),
                GitCloner.get(creds),
                role.is_admin()
        )
        self.repos = {}
        self.config_tab.signals.repos_updated.connect(self.signals.populate_tabs)

    def init_ui(self, window: 'QMainWindow'):
        self.ui = Ui_MainWindow()
        self.window = window
        self.ui.setupUi(window)
        self.ui.tab_widget.currentChanged.connect(self.signals.discard)
        self.setup_actions()
        self.populate_tabs()

    def update_creds(self, creds: 'api.ssh.SSHCreds'):
        self.creds = creds
        ssh = SSH.get(creds)
        self.config_tab.replace_ssh(
                RepoPackage(ssh),
                SelfPackage(ssh),
                GitCloner.get(creds))
        self.populate_tabs()

    def populate_tabs(self):
        self.ui.tab_widget.clear()
        self.repos.clear()
        for repo in self.config.get_repos():
            repo_tab = RepoPageController(repo.name, GitRepo.get(repo, self.creds))
            self.ui.tab_widget.addTab(repo_tab.widget, repo.name)
            self.repos[repo.name] = repo_tab
        self.ui.tab_widget.addTab(self.config_tab.widget, self.window.tr(self.CONFIG_TAB))
        self.check_enable_repo_menu(self.ui.tab_widget.currentIndex())

    def setup_actions(self):
        # disable repo menu on config tab
        self.ui.tab_widget.currentChanged.connect(self.signals.check_enable_repo_menu)
        self.ui.repo_fetch.triggered.connect(self.signals.fetch)
        self.ui.self_log_out.triggered.connect(self.signals.logged_out)
        self.ui.self_passwd.triggered.connect(self.signals.change_passwd)

        if self.role.is_admin():
            self.ui.users_manage.triggered.connect(self.signals.open_users)
            self.ui.repo_users.triggered.connect(self.signals.open_repo_users)
            self.ui.repo_push.triggered.connect(self.signals.push)
        else:
            self.ui.users_menu.menuAction().setVisible(False)
            self.ui.repo_users.setVisible(False)
            self.ui.repo_push.setVisible(False)

    def change_passwd(self):
        self_cmds = SelfPackage(SSH.get(self.creds))
        passwd, ok = QInputDialog.getText(
                self.window,
                self.window.tr('Password change'),
                self.window.tr('Password:'),
                QLineEdit.Password)
        if not ok:
            return

        try:
            self_cmds.passwd(passwd)
        except (InvalidPasswordError, CommandError) as ex:
            show_error(self.window, ex)
        else:
            QMessageBox.information(
                    self.window,
                    self.window.tr('Success'),
                    self.window.tr('Password changed successfully'))
            new_creds = self.creds.change_password(passwd)
            self.update_creds(new_creds)

    def fetch(self):
        repo_page = self.get_current_repo()
        repo_page.process_fetch()

    def push(self):
        repo_page = self.get_current_repo()
        repo_page.process_push()

    def open_repo_users(self):
        repo_name = self.get_current_repo().repo_name
        ssh = SSH.get(self.creds)
        repo_users = RepoUsersController(
                self.window,
                repo_name,
                UserPackage(ssh),
                AccessPackage(ssh))
        repo_users.dialog.exec()

    def open_users(self):
        users = self.get_user_controller()
        users.dialog.exec()

    def get_user_controller(self):
        ssh = SSH.get(self.creds)
        match self.role:
            case Role.Owner:
                return OwnerUserController(self.window, UserPackage(ssh), AdminPackage(ssh))
            case Role.Admin:
                return AdminUserController(self.window, UserPackage(ssh))
            case role:
                raise NotImplementedError(f'Unsupported role: {role}')

    def get_current_repo(self):
        idx = self.ui.tab_widget.currentIndex()
        if idx == self.ui.tab_widget.count() - 1:
            raise ValueError('Current page is not a repo')
        repo_name = self.ui.tab_widget.tabText(idx)
        return self.repos[repo_name]

    def check_enable_repo_menu(self, row):
        self.ui.repo_menu.setEnabled(row != self.ui.tab_widget.count() - 1)
