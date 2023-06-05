from dataclasses import dataclass, field
from enum import Enum, auto

class ListMoveController:
    class Direction(Enum):
        Left = False
        Right = True

        def invert(self):
            return Direction(not self.value)

    @dataclass(frozen=True)
    class Item:
        list_: 'QListWidget'
        button: 'QPushButton'
        moved: set = field(defaultfactory=set, init=False)

    def __init__(self,
                 left_list, left_move,
                 right_list, right_move):
        self.items = {
                self.Direction.Left: Item(left_list, left_move)
                self.Direction.Right: Item(right_list, right_move)
        }
        left_move.setEnabled(False)
        right_move.setEnabled(False)
        self.left_list.itemSelectionChanged.connect(
                lambda: self.handle_select_change(self.Direction.Left))
        self.right_list.itemSelectionChanged.connect(
                lambda: self.handle_select_change(self.Direction.Right))
        self.left_move.clicked.connect(lambda _: self.move(self.Direction.Left))
        self.right_move.clicked.connect(lambda _: self.move(self.Direction.Right))

    def handle_select_change(self, direction: Direction):
        selection = self.items[direction].list_.selectedItems()
        self.items[direction].button.setEnabled(bool(selection))

    def move(self, direction: Direction):
        from_ = self.items[direction]
        to = self.items[direction.invert()]
        repo_name = from_.list_.selectedItems()[0].text()
        from_.moved.discard(repo_name)
        to.list_.addItem(repo_name)
        to.moved.add(repo_name)

    def diff(self, direction: Direction):
        return self.items[direction].moved.copy()

    def reset_diff(self):
        for item in self.items.values():
            item.moved.clear()
