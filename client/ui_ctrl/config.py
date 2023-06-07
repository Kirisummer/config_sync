from shutil import rmtree
from platform import system

from PySide6.QtCore import QObject, QStandardPaths, Signal, Slot
from PySide6.QtWidgets import (
        QWidget, QMessageBox, QInputDialog, QDialogButtonBox, QListWidgetItem
)

from .list_move import ListMoveController
from .clone import CloneDialogController
from .errors import show_error
from .search import ListSearchController
from api.command_error import (
        RepoExistsError, InvalidRepoNameError, RepoNotFoundError, CommandError
)
from api.git import GitCommandError
from common import bullet_list
from ui import Ui_RepoConfigPage

class RepoConfigController:
    class Signals(QObject):
        repos_updated = Signal()

        def __init__(self, control):
            super().__init__()
            self.control = control

        @Slot(bool)
        def create_remote_dialog(self, clicked):
            self.control.create_remote_dialog()

        @Slot(bool)
        def delete_remote_dialog(self, clicked):
            self.control.delete_remote_dialog()

        @Slot()
        def update_delete_button(self):
            self.control.update_delete_button()

        @Slot(bool)
        def apply(self, clicked):
            self.control.apply()

        @Slot(bool)
        def discard(self, clicked):
            self.control.discard()

        @Slot(object) # list['common.Repo']
        def remote_clone(self, repos):
            self.control.remote_clone(repos)

        @Slot(str)
        def update_last_dir(self, path):
            self.control.update_last_dir(path)

    def __init__(self,
                 config: 'config.ConfigManager',
                 repo_cmds: 'api.commands.RepoPackage',
                 self_cmds: 'api.commands.SelfPackage',
                 git_cloner: 'api.git.GitCloner',
                 is_admin: bool):

        self.config = config
        self.repo_cmds = repo_cmds
        self.self_cmds = self_cmds
        self.git_cloner = git_cloner
        self.signals = self.Signals(self)

        # used for cloning dialog
        self.last_dir = self.get_default_dir()
        self.list_move = None

        # setup UI
        self.ui = Ui_RepoConfigPage()
        self.widget = QWidget()
        self.ui.setupUi(self.widget)

        self.local_search = ListSearchController(
                self.ui.local_search_box,
                self.ui.local_search_button,
                self.ui.local_list
        )
        self.remote_search = ListSearchController(
                self.ui.remote_search_box,
                self.ui.remote_search_button,
                self.ui.remote_list
        )

        self.populate_lists()

        # create list move controller
        # remove new and delete buttons for non-admins
        if not is_admin:
            self.ui.new_.hide()
            self.ui.delete_.hide()

        # signal connections
        self.ui.new_.clicked.connect(self.signals.create_remote_dialog)
        self.ui.delete_.clicked.connect(self.signals.delete_remote_dialog)
        self.ui.remote_list.itemSelectionChanged.connect(
                self.signals.update_delete_button)
        self.ui.apply.clicked.connect(self.signals.apply)
        self.ui.reset.clicked.connect(self.signals.discard)

    def replace_ssh(self,
                    repo_cmds: 'api.commands.RepoPackage',
                    self_cmds: 'api.commands.SelfPackage',
                    git_cloner: 'api.git.GitCloner'):
        self.repo_cmds = repo_cmds
        self.self_cmds = self_cmds
        self.git_cloner = git_cloner

    def populate_lists(self):
        self.ui.local_list.clear()
        local_repos = set(repo.name for repo in self.config.get_repos())
        self.ui.local_list.addItems(local_repos)

        self.ui.remote_list.clear()
        try:
            remote_repos = set(self.self_cmds.repos())
        except CommandError as ex:
            show_error(self.widget, ex)
        else:
            remote_repos -= local_repos
            self.ui.remote_list.addItems(remote_repos)

        if self.list_move:
            self.list_move.disconnect()
        self.list_move = ListMoveController(
                self.ui.local_list, self.ui.to_remotes,
                self.ui.remote_list, self.ui.to_locals
        )

    def apply(self):
        local_delete = self.list_move.diff(ListMoveController.Direction.Right)
        if local_delete:
            ok = self.local_delete_dialog(local_delete)
            if ok:
                self.local_delete(local_delete)

        remote_clone = self.list_move.diff(ListMoveController.Direction.Left)
        if remote_clone:
            clone = CloneDialogController(self.widget, self.last_dir, remote_clone)
            clone.signals.repo_paths_selected.connect(self.signals.remote_clone)
            clone.signals.directory_chosen.connect(self.signals.update_last_dir)
            clone.dialog.exec()

    def update_last_dir(self, path):
        self.last_dir = path

    def discard(self):
        self.populate_lists()

    def create_remote_dialog(self):
        remote_name, ok = QInputDialog.getText(
                self.widget,
                self.widget.tr('Create remote'),
                self.widget.tr('Name of new remote:')
        )
        
        if ok:
            if remote_name:
                try:
                    self.repo_cmds.create(remote_name)
                except (InvalidRepoNameError, RepoExistsError, CommandError) as ex:
                    show_error(self.widget, ex)
                else:
                    self.ui.remote_list.addItem(QListWidgetItem(remote_name))
            else:
                show_error(self.widget, InvalidRepoNameError(remote_name))

    def delete_remote_dialog(self):
        remote_name = self.ui.remote_list.selectedItems()[0].text()
        ok = QMessageBox.question(
                self.widget,
                self.widget.tr('Remote repository deletion'),
                self.widget.tr('Remove remote repository {}?').format(remote_name)
        )
        if ok == QMessageBox.StandardButton.Yes:
            err = None
            try:
                self.repo_cmds.delete(remote_name)
            except (RepoNotFoundError, CommandError) as ex:
                show_error(self.widget, ex)

    def local_delete_dialog(self, local_delete: set[str]):
        repo_text = bullet_list(local_delete)
        return QMessageBox.question(
                self.widget,
                self.widget.tr('Local repository deletion'),
                self.widget.tr('Delete following repositories?') + repo_text
        )

    def local_delete(self, local_delete: set[str]):
        repos = self.config.get_repos()
        not_deleted = set()
        deleted = set()
        for repo in repos:
            if repo.name in local_delete:
                try:
                    rmtree(repo.path)
                    deleted.add(repo.name)
                except OsError:
                    not_deleted(repo.name)
        self.config.delete_repos(deleted)
        not_found = local_delete - deleted - not_deleted

        if not_deleted or not_found:
            msg = []
            if not_deleted:
                msg.append(self.widget.tr('Following repositories were not deleted:'))
                msg.append(bullet_list(not_deleted))
            if not_found:
                msg.append(self.widget.tr('Following repositories were not found:'))
                msg.append(bullet_list(not_found))
            QMessageBox.critical(
                    self.widget,
                    self.widget.tr('Deletion error'),
                    '\n'.join(msg)
            )
        else:
            QMessageBox.information(
                    self.widget,
                    self.widget.tr('Success'),
                    self.widget.tr('Repositories were deleted successfully')
            )
        self.signals.repos_updated.emit()

    def remote_clone(self, repos: list['common.Repo']):
        not_cloned = set()
        for repo in repos:
            try:
                self.git_cloner.clone(repo)
                self.config.add_repo(repo)
            except GitCommandError as ex:
                QMessageBox.critical(
                        self.widget,
                        self.widget.tr('Git error'),
                        ex.message
                )
                not_cloned.add(repo.name)
        if not_cloned:
            QMessageBox.critical(
                    self.widget,
                    self.widget.tr('Cloning failed'),
                    self.widget.tr('Failed to clone repositories:') + bullet_list(not_cloned)
            )
        else:
            QMessageBox.information(
                    self.widget,
                    self.widget.tr('Success'),
                    self.widget.tr('Repositories were cloned successfully')
            )
        self.signals.repos_updated.emit()
        self.populate_lists()

    def update_delete_button(self):
        remote_selection = self.ui.remote_list.selectedItems()
        self.ui.delete_.setEnabled(bool(remote_selection))

    @staticmethod
    def get_default_dir():
        match system():
            case 'Linux':
                return QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
            case 'Windows':
                return QStandardPaths.standardLocations(QStandardPaths.DesktopLocation)[0]
            case os_name:
                raise NotImplementedError(f'Unsupported OS: {os_name}')
