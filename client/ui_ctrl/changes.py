from dataclasses import dataclass, field
from typing import ClassVar

from PySide6.QtCore import QObject, Qt, QPoint, Signal, Slot
from PySide6.QtWidgets import QMenu, QMessageBox, QTableWidgetItem, QHeaderView

class ChangeController:
    class Signals(QObject):
        checked_out = Signal(str)
        change_switched = Signal(str)

    HEAD_MARKER = '*'
    HEAD_COL = 0
    SUMMARY_COL = 1

    def __init__(self,
                 changes: 'QTableWidget',
                 heads: 'QComboBox',
                 repo: 'api.git.Repo'):
        self.changes = changes
        self.heads = heads
        self.repo = repo

        # vertical header sizes
        header = self.changes.verticalHeader()
        header.setFixedWidth(70)
        header.setSectionResizeMode(QHeaderView.Fixed)
        self.changes.setColumnWidth(self.HEAD_COL, 20)

        self.populate_heads()
        self.heads.currentTextChanged.connect(lambda head: self.populate_commits(head))
        self.changes.itemSelectionChanged.connect(lambda: self.handle_commit_change())
        self.populate_commits(self.heads.currentText()) # populate with HEAD
        self.signals = self.Signals()

    def set_repo(self, repo: 'api.git.Repo'):
        self.repo = repo

    def handle_commit_change(self):
        indexes = self.changes.selectedIndexes()
        if indexes:
            row_idx = indexes[0].row()
            revision = self.changes.verticalHeaderItem(row_idx).text()
            self.signals.change_switched.emit(revision)

    def get_selected_revision(self):
        return self.changes.verticalHeaderItem(self.changes.currentRow()).text()

    def populate_heads(self):
        self.heads.clear()
        self.heads.addItem('HEAD')
        self.heads.addItems(self.repo.branches())

    def populate_commits(self, revision):
        self.changes.setRowCount(0)
        head_hash = self.repo.head()
        for commit_hash, summary in self.repo.revision_log(revision):
            row_idx = self.changes.rowCount()
            self.changes.insertRow(row_idx)
            self.changes.setVerticalHeaderItem(row_idx, QTableWidgetItem(commit_hash))
            item = QTableWidgetItem(summary)
            self.changes.setItem(row_idx, self.SUMMARY_COL, QTableWidgetItem(summary))
            if commit_hash == head_hash:
                self.changes.setItem(
                        row_idx, self.HEAD_COL, QTableWidgetItem(self.HEAD_MARKER))


    def checkout(self, revision):
        result = QMessageBox.question(
                parent=self.changes,
                title=self.changes.tr('Checkout'),
                text=self.changes.tr('Your changes will be discarded. Checkout ') + revision + '?'
        )
        if result == QMessageBox.StandardButton.Yes:
            self.repo.checkout(revision)
            self.signals.checked_out.emit(revision)

    def handle_context_menu(self, pos: QPoint):
        item = self.changes.itemAt(pos)
        revision = self.changes.verticalHeaderItem(row).text()
        menu = QMenu(self.changes)
        menu.addAction(self.changes.tr('Checkout'), partial(self.checkout, revision=revision))
        menu.exec(pos)
