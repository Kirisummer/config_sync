from .search import TableSearchController
from .changes import ChangeController

from bigtree import list_to_tree, preorder_iter
from PySide6.QtCore import QObject, Qt, Slot
from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QInputDialog, QMessageBox

from api.git import GitRepo, GitCommandError
from config import Repo
from ui.repo import Ui_RepoPage

class RepoPageController:
    class Signals(QObject):
        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(str)
        def change_switched(self, revision):
            self.control.change_switched(revision)

        @Slot(QTreeWidgetItem, QTreeWidgetItem)
        def file_switched(self, curr, prev):
            self.control.file_switched(curr)

    PATH_DATA = (0, Qt.UserRole)
    COMMIT_SUMMARY_COL = 1

    def __init__(self, repo_name: Repo, repo: 'api.git.Repo'):
        super().__init__()

        self.repo_name = repo_name
        self.repo = repo
        self.signals = self.Signals(self)

        # setup UI's default state
        self.ui = Ui_RepoPage()
        self.widget = QWidget()
        self.ui.setupUi(self.widget)
        self.commit_search = TableSearchController(
                table_widget=self.ui.changes,
                search_col=self.COMMIT_SUMMARY_COL,
                search_box=self.ui.changes_search_box,
                search_btn=self.ui.changes_search_btn
        )
        self.change_controller = ChangeController(
                self.ui.changes, self.ui.head_select, self.repo)
        self.ui.commit_msg_widget.hide()
        self.ui.diff_widget.hide()

        # actions
        self.change_controller.signals.change_switched.connect(
                self.signals.change_switched)
        self.ui.files.currentItemChanged.connect(
                self.signals.file_switched)

    def set_repo(self, repo: 'api.git.GitRepo'):
        self.repo = repo
        self.change_controller.set_repo(repo)

    def process_refresh(self):
        self.change_controller.populate_heads()

    def process_fetch(self):
        try:
            self.repo.fetch()
        except GitCommandError as ex:
            QMessageBox.critical(
                    self.widget,
                    self.widget.tr('Git error'),
                    ex.message
            )
        else:
            QMessageBox.information(
                    self.widget,
                    self.widget.tr('Fetch complete'),
                    self.widget.tr('Fetch was completed successfully')
            )
        self.change_controller.populate_heads()

    def process_push(self):
        if not self.repo.head():
            QMessageBox.critical(
                    self.widget,
                    self.widget.tr('Empty repository'),
                    self.widget.tr('Cannot push: the repository is empty')
            )
            return
        refs = set(self.repo.refs())
        remote = self.repo.remote()
        for branch in self.repo.branches():
            refs.add(f'{remote}/{branch}')
        ref, ok = QInputDialog.getItem(
                self.widget,
                self.widget.tr('Push'),
                self.widget.tr('Push to:'),
                refs, editable=False
        )
        if ok and ref:
            try:
                self.repo.push(ref)
            except GitCommandError as ex:
                QMessageBox.critical(
                        self.widget,
                        self.widget.tr('Git error'),
                        ex.message
                )
            else:
                QMessageBox.information(
                        self.widget,
                        self.widget.tr('Success'),
                        self.widget.tr('Pushed successfully')
                )
        self.change_controller.populate_heads()

    def change_switched(self, revision):
        files, commit_msg = self.repo.commit_stat(revision)
        self.populate_files(files)
        self.ui.commit_msg.setPlainText(commit_msg)

        self.ui.diff_widget.hide()
        self.ui.no_file.show()
        self.ui.no_commit.hide()
        self.ui.commit_msg_widget.show()

    def file_switched(self, new_item):
        if new_item is None:
            return
        revision = self.change_controller.get_selected_revision()
        diff = self.repo.diff(revision, new_item.data(*self.PATH_DATA))
        self.ui.diff.setPlainText(diff)
        self.ui.diff_widget.show()
        self.ui.no_file.hide()

    def populate_files(self, files):
        self.ui.files.clear()
        if files:
            root = list_to_tree(map(lambda file: f'{self.repo_name}/{file}', files))
            root_item = self.tree_item(self.repo_name)
            root.set_attrs({'item': root_item})
            for node in preorder_iter(root):
                if node == root:
                    continue
                file_path = node.path_name.removeprefix(f'/{self.repo_name}/')
                item = self.tree_item(node.name, file_path)
                node.set_attrs({'item': item})
                node.parent.get_attr('item').addChild(item)
            self.ui.files.addTopLevelItem(root_item)
            self.ui.files.expandAll()

    @classmethod
    def tree_item(cls, name, path=None):
        item = QTreeWidgetItem()
        item.setText(0, name)
        if path:
            item.setData(*cls.PATH_DATA, path)
        return item
