from .search import TableSearchController
from .changes import ChangeController

from config import Repo
from ui.repo import Ui_RepoPage

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget

from api.git import GitRepo
from bigtree import list_to_tree

class RepoPageController(QObject):
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
        header.setFixedHeight(header.sizeHint().height())

        # actions
        self.change_controller.change_switched.connect(self.change_switched)
        self.ui.files.currentItemChanged.connect(self.file_switched)

    def set_ssh(self, ssh: 'api.ssh.SSH'):
        self.ssh = ssh
        self.git = GitRepo(repo.path, self.ssh)
        self.change_controller.set_git(self.git)

    def change_switched(self, revision):
        self.populate_files(revision)
        self.ui.commit_msg.setText(self.git.commit_message(revision))

        self.ui.diff_widget.hide()
        self.ui.no_diff.show()
        self.ui.no_commit.hide()
        self.ui.commit_msg_widget.show()

    def file_switched(self, prev_item, new_item):
        revision = self.change_controller.get_selected_revision()
        self.git.diff(revision, new_item.data())
        self.ui.diff_widget.show()
        self.ui.no_diff.hide()

    def populate_files(self, revision):
        files = self.git.commit_files(revision)
        root = list_to_tree(map(lambda file: f'{self.repo.name}/{file}', files))
        root_item = QTreeWidgetItem()
        root_item.setText(self.repo.name)
        root.set_attrs({'item': root_item})
        for node in preorder_iter(root):
            if node == root:
                continue
            item = QTreeWidgetItem()
            item.setText(node.name)
            item.setData(node.path_name.lstrip(f'{self.repo.name}/'))
            node.set_attrs({'item': item})
            node.parent.get_attr('item').addChild(item)
        self.ui.files.addTopLevelItem(root_item)
