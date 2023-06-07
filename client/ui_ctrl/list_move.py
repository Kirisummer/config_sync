from PySide6.QtCore import QObject, Slot

from dataclasses import dataclass, field, astuple
from enum import Enum, auto

class ListMoveController:
    class Signals(QObject):
        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(int)
        def handle_left_select_change(self, row):
            self.control.handle_select_change(self.control.Direction.Left, row)

        @Slot(int)
        def handle_right_select_change(self, row):
            self.control.handle_select_change(self.control.Direction.Right, row)

        @Slot(bool)
        def right_move(self, clicked):
            self.control.move(self.control.Direction.Right)

        @Slot(bool)
        def left_move(self, clicked):
            self.control.move(self.control.Direction.Left)

    class Direction(Enum):
        Left = False
        Right = True

        def invert(self):
            return ListMoveController.Direction(not self.value)

    @dataclass(frozen=True)
    class Item:
        list_: 'QListWidget'
        button: 'QPushButton'
        moved: set = field(default_factory=set, init=False)

    def __init__(self,
                 left_list, left_move,
                 right_list, right_move):
        self.items = {
                self.Direction.Left: self.Item(left_list, left_move),
                self.Direction.Right: self.Item(right_list, right_move)
        }
        left_move.setEnabled(False)
        right_move.setEnabled(False)

        self.signals = self.Signals(self)
        left_list.currentRowChanged.connect(self.signals.handle_left_select_change)
        right_list.currentRowChanged.connect(self.signals.handle_right_select_change)
        left_move.clicked.connect(self.signals.right_move)
        right_move.clicked.connect(self.signals.left_move)

    def handle_select_change(self, direction: Direction, row):
        self.items[direction].button.setEnabled(row != -1)

    def move(self, direction: Direction):
        from_ = self.items[direction.invert()]
        to = self.items[direction]

        item = from_.list_.takeItem(from_.list_.currentRow())
        repo_name = item.text()

        from_.moved.discard(repo_name)
        to.list_.addItem(repo_name)
        to.moved.add(repo_name)

    def diff(self, direction: Direction):
        return self.items[direction].moved.copy()

    def reset_diff(self):
        for item in self.items.values():
            item.moved.clear()

    def disconnect(self):
        left_list = self.items[self.Direction.Left].list_
        left_move = self.items[self.Direction.Left].button
        right_list = self.items[self.Direction.Right].list_
        right_move = self.items[self.Direction.Right].button

        left_list.currentRowChanged.disconnect(self.signals.handle_left_select_change)
        right_list.currentRowChanged.disconnect(self.signals.handle_right_select_change)
        left_move.clicked.disconnect(self.signals.right_move)
        right_move.clicked.disconnect(self.signals.left_move)
