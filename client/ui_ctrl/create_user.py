from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QDialog

from ui import Ui_CreateUser

class CreateUserController:
    class Signals(QObject):
        creds_entered = Signal((str, str))

        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(bool)
        def emit_creds(self, clicked):
            self.creds_entered.emit(
                    self.control.ui.login.text(),
                    self.control.ui.password.text()
            )

    def __init__(self, parent: 'QWidget'):
        self.dialog = QDialog()
        self.ui = Ui_CreateUser()
        self.ui.setupUi(self.dialog)
        self.signals = self.Signals(self)

        self.ui.create.clicked.connect(self.signals.emit_creds)
        self.ui.create.clicked.connect(self.dialog.accept)
