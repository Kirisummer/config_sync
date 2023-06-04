from .search import TableSearchController
from .changes import ChangeController

from bigtree import list_to_tree, preorder_iter
from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QWidget, QHeaderView, QTreeWidgetItem

from api.git import GitRepo
from config import Repo
from ui.repo import Ui_RepoPage


class RepoPageController:
    
    PATH_DATA = (0, Qt.UserRole)

    def __init__(self, repo: Repo, ssh: 'api.ssh.SSH'):
        super().__init__()

        self.repo = repo
        self.ssh = ssh
        self.git = GitRepo(repo, self.ssh)

        self.ui = Ui_RepoPage()
        self.widget = QWidget()

        # setup UI's default state
        self.ui.setupUi(self.widget)
        self.commit_search = TableSearchController(
                table_widget=self.ui.changes,
                search_col=0,
                search_box=self.ui.changes_search_box,
                search_btn=self.ui.changes_search_btn
        )
        self.change_controller = ChangeController(self.ui.changes, self.git)
        self.ui.commit_msg_widget.hide()
        self.ui.diff_widget.hide()

        # vertical header size
        header = self.ui.changes.verticalHeader()
        header.setFixedWidth(70)
        header.setSectionResizeMode(QHeaderView.Fixed)

        # actions
        self.change_controller.signals.change_switched.connect(
                lambda revision: self.change_switched(revision)
        )
        self.ui.files.currentItemChanged.connect(
                lambda file_path, _: self.file_switched(file_path)
        )

    def set_ssh(self, ssh: 'api.ssh.SSH'):
        self.ssh = ssh
        self.git = GitRepo(repo.path, self.ssh)
        self.change_controller.set_git(self.git)

    def change_switched(self, revision):
        files, commit_msg = self.git.commit_stat(revision)
        self.populate_files(files)
        self.ui.commit_msg.setPlainText(commit_msg)

        self.ui.diff_widget.hide()
        self.ui.no_file.show()
        self.ui.no_commit.hide()
        self.ui.commit_msg_widget.show()

    def file_switched(self, new_item):
        revision = self.change_controller.get_selected_revision()
        diff = self.git.diff(revision, new_item.data(*self.PATH_DATA))
        self.ui.diff.setPlainText(diff)
        self.ui.diff_widget.show()
        self.ui.no_file.hide()

    def populate_files(self, files):
        self.ui.files.clear()
        root = list_to_tree(map(lambda file: f'{self.repo.name}/{file}', files))
        root_item = self.tree_item(self.repo.name)
        root.set_attrs({'item': root_item})
        for node in preorder_iter(root):
            if node == root:
                continue
            file_path = node.path_name.removeprefix(f'/{self.repo.name}/')
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
