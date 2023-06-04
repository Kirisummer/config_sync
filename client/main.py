import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from api.ssh import SSH
from ui_ctrl.login import LoginController
from ui_ctrl.repo import RepoPageController
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

    def on_login(self, role: str, ssh: SSH):
        # self.main = MainWindowController(role, ssh)
        # self.main.logged_out.connect(self.on_logout)
        # self.main.password_changed.connect(self.on_password_changed)
        # for repo in self.config.get_repos():
        #     control = RepoPageController(repo, ssh)
        #     self.main.add_repo(control)
        self.main_ui = Ui_MainWindow()
        self.main_ui.setupUi(self.window)
        for repo in self.config.get_repos():
            control = RepoPageController(repo, ssh)
            self.main_ui.tab_widget.addTab(control.widget, repo.name)

if __name__ == '__main__':
    app = Application(sys.argv)
    app.login.ui.password.setText(sys.argv[1])
    app.login.ui.login_button.click()
    sys.exit(app.run())

