from dataclasses import dataclass, field
from functools import partial

from PySide6.QtCore import QObject, Slot

@dataclass(frozen=True)
class SearchController:
    class Signals(QObject):
        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot()
        def perform_search(self):
            self.control.perform_search()

    search_box: 'PySide6.QtWidgets.QLineEdit'
    search_btn: 'PySide6.QtWidgets.QToolButton'
    signals: Signals = field(init=False)

    def __post_init__(self):
        super().__setattr__('signals', self.Signals(self))
        self.search_btn.clicked.connect(self.signals.perform_search)
        self.search_box.returnPressed.connect(self.signals.perform_search)

    def perform_search(self):
        query = self.search_box.text()
        for item in self.items:
            item.set_hidden(query not in item.text)

    def clear_filter(self):
        self.search_box.clear()
        for item in self.items:
            item.setHidden(False)

@dataclass(frozen=True)
class ListSearchController(SearchController):
    list_widget: 'PySide6.QtWidgets.QListWidget'

    @dataclass(frozen=True)
    class ListSearchItem:
        list_item: 'QListWidgetItem'

        @property
        def text(self):
            return self.list_item.text()

        def set_hidden(self, hidden: bool):
            self.list_item.setHidden(hidden)

    @property
    def items(self):
        def make_item(idx):
            return self.ListSearchItem(self.list_widget.item(idx))
        return map(make_item, range(self.list_widget.count()))

@dataclass(frozen=True)
class TableSearchController(SearchController):
    table_widget: 'PySide6.QtWidgets.QTableWidget'
    search_col: int

    @dataclass(frozen=True)
    class TableSearchItem:
        table_widget: 'PySide6.QtWidgets.QTableWidget'
        row: int
        search_col: int

        @property
        def text(self):
            return self.table_widget.item(self.row, self.search_col).text()

        def set_hidden(self, hidden: bool):
            self.table_widget.setRowHidden(self.row, hidden)
    
    @property
    def items(self):
        def make_item(row_idx):
            return self.TableSearchItem(self.table_widget, row_idx, self.search_col)
        return map(make_item, range(self.table_widget.rowCount()))
