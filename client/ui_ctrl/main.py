from PySide6.QtCore import QObject, Slot

from .config import RepoConfigController
from .repo import RepoPageController
from .user_admin import AdminUserController
from .user_owner import OwnerUserController
from .repo_users import RepoUsersController

from api.commands import AdminPackage, AccessPackage, RepoPackage, SelfPackage, UserPackage
from api.ssh import SSH
from api.git import GitRepo, GitCloner
from common import Role
from ui import Ui_MainWindow

class MainController:
    class Signals(QObject):
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

        for repo_tab in self.repo_tabs:
            repo_tab.set_repo(GitRepo.get(creds))

        ssh = SSH.get(creds)
        self.config_conn.replace_ssh(
                RepoPackage(ssh),
                SelfPackage(ssh),
                GitCloner.get(creds)
        )

    def populate_tabs(self):
        self.ui.tab_widget.clear()
        for repo in self.config.get_repos():
            repo_tab = RepoPageController(repo.name, GitRepo.get(repo, self.creds))
            self.ui.tab_widget.addTab(repo_tab.widget, repo.name)
        self.ui.tab_widget.addTab(self.config_tab.widget, self.window.tr(self.CONFIG_TAB))
        self.check_enable_repo_menu(self.ui.tab_widget.currentIndex())

    def setup_actions(self):
        # disable repo menu on config tab
        self.ui.tab_widget.currentChanged.connect(self.signals.check_enable_repo_menu)

        if self.role.is_admin():
            self.ui.users_manage.triggered.connect(self.signals.open_users)
            self.ui.repo_users.triggered.connect(self.signals.open_repo_users)
        else:
            print('not admin')
            self.ui.users_menu.menuAction().setVisible(False)
            self.ui.repo_users.setVisible(False)

    def open_users(self):
        users = self.get_user_controller()
        users.dialog.exec()

    def open_repo_users(self):
        repo_name = self.ui.tab_widget.tabText(self.ui.tab_widget.currentIndex())
        ssh = SSH.get(self.creds)
        repo_users = RepoUsersController(
                self.window,
                repo_name,
                UserPackage(ssh),
                AccessPackage(ssh))
        repo_users.dialog.exec()

    def get_user_controller(self):
        ssh = SSH.get(self.creds)
        match self.role:
            case Role.Owner:
                return OwnerUserController(self.window, UserPackage(ssh), AdminPackage(ssh))
            case Role.Admin:
                return AdminUserController(self.window, UserPackage(ssh))
            case role:
                raise NotImplementedError(f'Unsupported role: {role}')

    def check_enable_repo_menu(self, row):
        self.ui.repo_menu.setEnabled(row != self.ui.tab_widget.count() - 1)
