from PySide6.QtCore import QObject, Slot

from .config import RepoConfigController
from .repo import RepoPageController
from .user_owner import OwnerUserController

from api.commands import AdminPackage, RepoPackage, SelfPackage, UserPackage
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
        def open_users_dialog(self, checked):
            self.control.open_users_dialog()

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

    def open_users_dialog(self):
        users = self.get_user_controller()
        users.dialog.exec()

    def setup_actions(self):
        if self.role.is_admin():
            users = self.get_user_controller()
            self.ui.users_manage.triggered.connect(self.signals.open_users_dialog)

    def get_user_controller(self):
        ssh = SSH.get(self.creds)
        match self.role:
            case Role.Owner:
                return OwnerUserController(UserPackage(ssh), AdminPackage(ssh))
            case role:
                raise NotImplementedError(f'Unsupported role: {role}')
