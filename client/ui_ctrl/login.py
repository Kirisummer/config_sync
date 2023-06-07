from dataclasses import dataclass, field

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QWidget

from api.ssh import SSH, SSHCreds
from api.commands import SelfPackage
from common import Role
from ui import Ui_Login

class LoginController:
    class Signals(QObject):
        logged_in = Signal((Role, SSHCreds))

    def __init__(self, config: 'config.ConfigManager'):
        self.config = config
        self.signals = self.Signals()

    def init_ui(self, window: 'QMainWindow'):
        self.ui = Ui_Login()
        self.window = window
        self.window.menuBar().setVisible(False)
        self.ui.setupUi(self.window)

        last_creds = self.config.get_last_creds()
        self.set_ui_creds(self.ui, last_creds)
        self.ui.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        creds = self.get_ui_creds(self.ui)
        ssh = SSH.get(creds)
        self_pkg = SelfPackage(ssh)
        role = Role(self_pkg.role())
        self.config.save_creds(creds)
        self.signals.logged_in.emit(role, creds)

    @staticmethod
    def set_ui_creds(ui: Ui_Login, creds: SSHCreds):
        if creds.host:
            ui.host.setText(creds.host)
        if creds.port is not None:
            ui.port.setValue(creds.port)
        if creds.login:
            ui.login.setText(creds.login)

    @staticmethod
    def get_ui_creds(ui: Ui_Login):
        return SSHCreds(
                ui.login.text(),
                ui.password.text(),
                ui.host.text(),
                ui.port.value()
        )
