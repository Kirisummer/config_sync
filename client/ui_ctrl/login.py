from dataclasses import dataclass, field

from api.ssh import SSH, SSHCreds
from api.commands import SelfPackage

from PySide6.QtCore import Signal, QObject
from PySide6.QtWidgets import QWidget

@dataclass(frozen=True)
class LoginController:
    class Signals(QObject):
        logged_in = Signal((str, SSH))

    ui: 'ui.Ui_Login'
    config: 'config.ConfigManager'
    widget: QWidget = field(default_factory=QWidget, init=False)
    signals: Signals = field(default_factory=Signals, init=False)

    def __post_init__(self):
        self.ui.setupUi(self.widget)
        last_creds = self.config.get_last_creds()
        self.set_ui_creds(last_creds)
        self.ui.login_button.clicked.connect(self.handle_login)

    def handle_login(self):
        creds = self.get_ui_creds()
        ssh = SSH.get(creds)
        self_pkg = SelfPackage(ssh)
        role = self_pkg.role()
        self.config.save_creds(creds)
        self.signals.logged_in.emit(role, ssh)

    def set_ui_creds(self, creds: SSHCreds):
        if creds.host:
            self.ui.host.setText(creds.host)
        if creds.port is not None:
            self.ui.port.setValue(creds.port)
        if creds.login:
            self.ui.login.setText(creds.login)

    def get_ui_creds(self):
        return SSHCreds(
                self.ui.login.text(),
                self.ui.password.text(),
                self.ui.host.text(),
                self.ui.port.value()
        )
