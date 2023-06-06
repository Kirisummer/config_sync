from PySide6.QtCore import QObject

from api.commands import RepoPackage, SelfPackage
from api.ssh import SSH
from api.git import GitRepo, GitCloner
from ui import Ui_MainWindow
from .repo_config import RepoConfigController
from .repo import RepoPageController

class MainController:
    class Signals(QObject):
        pass

    CONFIG_TAB = 'Repository management'

    def __init__(self,
                 role: 'common.Role',
                 config: 'config.ConfigManager',
                 creds: 'api.ssh.SSHCreds'):
        self.config = config
        self.creds = creds

        ssh = SSH.get(creds)
        self.config_tab = RepoConfigController(
                self.config,
                RepoPackage(ssh),
                SelfPackage(ssh),
                GitCloner.get(creds),
                role.is_admin()
        )
        self.config_tab.signals.repos_updated.connect(lambda: self.populate_tabs())

    def init_ui(self, window: 'QMainWindow'):
        self.ui = Ui_MainWindow()
        self.window = window
        self.ui.setupUi(window)
        self.ui.tab_widget.currentChanged.connect(lambda _: self.config_tab.discard())
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
