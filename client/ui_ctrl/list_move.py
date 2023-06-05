from dataclasses import dataclass, field
from enum import Enum, auto

class ListMoveController:
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
        left_list.currentRowChanged.connect(
                lambda row: self.handle_select_change(self.Direction.Left, row))
        right_list.currentRowChanged.connect(
                lambda row: self.handle_select_change(self.Direction.Right, row))
        left_move.clicked.connect(lambda _: self.move(self.Direction.Left))
        right_move.clicked.connect(lambda _: self.move(self.Direction.Right))

    def handle_select_change(self, direction: Direction, row):
        self.items[direction].button.setEnabled(row != -1)

    def move(self, direction: Direction):
        from_ = self.items[direction]
        to = self.items[direction.invert()]

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
