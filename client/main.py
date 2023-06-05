import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from api.git import GitRepo, GitCloner
from api.ssh import SSH
from api.commands import RepoPackage, SelfPackage

from ui_ctrl.login import LoginController
from ui_ctrl.repo import RepoPageController
from ui_ctrl.repo_config import RepoConfigController

from ui import Ui_MainWindow
from config import ConfigManager

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.window = QMainWindow()
        self.config = ConfigManager('conf.toml')
        self.login = LoginController(self.config)
        self.window.setCentralWidget(self.login.widget)
        self.login.signals.logged_in.connect(self.on_login)

    def run(self):
        self.window.show()
        return self.exec()

    def on_login(self, role: str, creds: 'api.ssh.SSHCreds'):
        # self.main = MainWindowController(role, ssh)
        # self.main.logged_out.connect(self.on_logout)
        # self.main.password_changed.connect(self.on_password_changed)
        # for repo in self.config.get_repos():
        #     control = RepoPageController(repo, ssh)
        #     self.main.add_repo(control)
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self.window)
        for repo in self.config.get_repos():
            control = RepoPageController(repo.name, GitRepo.get(repo, creds))
            self.main_ui.tab_widget.addTab(control.widget, repo.name)
        ssh = SSH.get(creds)
        config = RepoConfigController(
                self.config, 
                RepoPackage(ssh),
                SelfPackage(ssh),
                GitCloner.get(creds),
                is_admin=True
        )
        self.main_ui.tab_widget.addTab(config.widget, self.tr('Repository configuration'))

if __name__ == '__main__':
    app = Application(sys.argv)
    app.login.ui.password.setText(sys.argv[1])
    app.login.ui.login_button.click()
    sys.exit(app.run())

