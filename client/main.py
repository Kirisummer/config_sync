import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from config import ConfigManager
from ui_ctrl.login import LoginController
from ui_ctrl.main import MainController
from ui import Ui_MainWindow

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

    def on_login(self, role: 'common.Role', creds: 'api.ssh.SSHCreds'):
        self.main = MainController(role, self.config, creds)
        self.main.init_ui(self.window)

if __name__ == '__main__':
    app = Application(sys.argv)
    if len(sys.argv) > 1:
        app.login.ui.password.setText(sys.argv[1])
        app.login.ui.login_button.click()
    sys.exit(app.run())

