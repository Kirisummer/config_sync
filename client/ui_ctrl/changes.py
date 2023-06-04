from dataclasses import dataclass, field
from typing import ClassVar

from PySide6.QtCore import QObject, Signal, Slot, Qt, QPoint
from PySide6.QtWidgets import QMenu, QMessageBox, QTableWidgetItem


class ChangeController:
    class Signals(QObject):
        checked_out = Signal(str)
        change_switched = Signal(str)

    def __init__(self, changes: 'QTableWidget', git: 'api.git.GitRepo'):
        self.changes = changes
        self.git = git
        self.populate(self.git.head())
        self.changes.itemSelectionChanged.connect(lambda: self.handle_select_change())
        self.signals = self.Signals()

    def set_git(self, git: 'api.git.GitRepo'):
        self.git = git

    def handle_select_change(self):
        indexes = self.changes.selectedIndexes()
        if indexes:
            row_idx = indexes[0].row()
            revision = self.changes.verticalHeaderItem(row_idx).text()
            self.signals.change_switched.emit(revision)

    def get_selected_revision(self):
        return self.changes.verticalHeaderItem(self.changes.currentRow()).text()

    def populate(self, revision):
        self.changes.clear()
        for commit_hash, summary in self.git.revision_log(revision):
            row_idx = self.changes.rowCount()
            self.changes.insertRow(row_idx)
            self.changes.setVerticalHeaderItem(row_idx, QTableWidgetItem(commit_hash))
            item = QTableWidgetItem(summary)
            self.changes.setItem(row_idx, 0, QTableWidgetItem(summary))

    def checkout(self, revision):
        result = QMessageBox.question(
                parent=self.changes,
                title=self.changes.tr('Checkout'),
                text=self.changes.tr('Your changes will be discarded. Checkout ') + revision + '?'
        )
        if result == QMessageBox.StandardButton.Yes:
            self.git.checkout(revision)
            self.signals.checked_out.emit(revision)

    def handle_context_menu(self, pos: QPoint):
        item = self.changes.itemAt(pos)
        revision = self.changes.verticalHeaderItem(row).text()
        menu = QMenu(self.changes)
        menu.addAction(self.changes.tr('Checkout'), partial(self.checkout, revision=revision))
        menu.exec(pos)
