from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QWidget, QDialog, QTableWidgetItem, QFileDialog, QMessageBox

from config import Repo
from ui import Ui_CloneDialog

class CloneDialogController:

    NAME_COL = 0
    PATH_COL = 1

    class Signals(QObject):
        repo_paths_selected = Signal((object,)) # list['common.Repo'])
        directory_chosen = Signal((str,))

        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(int, int)
        def try_unlock_clone(self, row, col):
            self.control.try_unlock_clone()

        @Slot(int, int)
        def handle_double_block(self, row, col):
            self.control.handle_double_click(row, col)

        @Slot(bool)
        def accept_dialog(self, clicked):
            self.control.accept_dialog()

    def __init__(self, parent: QWidget, last_dir: str, repos: set[str]):
        self.dialog = QDialog(parent)
        self.ui = Ui_CloneDialog()
        self.ui.setupUi(self.dialog)
        self.signals = self.Signals(self)

        self.populate_table(repos)
        self.last_dir = last_dir
        self.ui.clone.setEnabled(False)

        self.ui.repo_table.cellChanged.connect(self.signals.try_unlock_clone)
        self.ui.repo_table.cellDoubleClicked.connect(self.signals.handle_double_click)
        self.ui.clone.clicked.connect(self.signals.accept_dialog)
        self.ui.cancel.clicked.connect(self.dialog.reject)

    def accept_dialog(self):
        repos = []
        for row in range(self.ui.repo_table.rowCount()):
            repo = Repo(
                    self.ui.repo_table.item(row, self.NAME_COL).text(),
                    self.ui.repo_table.item(row, self.PATH_COL).text()
            )
            repos.append(repo)
        self.dialog.accept()
        self.signals.repo_paths_selected.emit(repos)

    def populate_table(self, repos: set[str]):
        for repo in repos:
            row = self.ui.repo_table.rowCount()
            self.ui.repo_table.insertRow(row)
            self.ui.repo_table.setItem(row, self.NAME_COL, QTableWidgetItem(repo))

    def handle_double_click(self, row, col):
        if col != self.PATH_COL:
            return
        repo_name = self.ui.repo_table.item(row, self.NAME_COL).text()
        dir_path = QFileDialog.getExistingDirectory(
                self.dialog,
                self.dialog.tr('Select a directory for repo to clone to'),
                self.last_dir)
        if dir_path:
            self.last_dir = dir_path
            self.signals.directory_chosen.emit(dir_path)

            repo_path = Path(dir_path) / repo_name
            if repo_path.exists():
                QMessageBox.critical(
                        self.dialog,
                        self.dialog.tr('Path exists'),
                        ' '.join((repo_path, self.dialog.tr('already exists')))
                )

            self.ui.repo_table.setItem(
                    row, self.PATH_COL, QTableWidgetItem(str(repo_path)))

    def try_unlock_clone(self):
        for row in range(self.ui.repo_table.rowCount()):
            if not self.ui.repo_table.item(row, self.PATH_COL).text():
                break
        else:
            self.ui.clone.setEnabled(True)
