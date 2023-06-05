from shutil import rmtree

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget, QMessageBox, QInputDialog

from .list_move import ListMoveController
from api.command_error import (
        RepoExists, InvalidRepoName, RepoNotFound, CommandError
)
from api.git import GitCommandError
from ui import Ui_RepoConfigPage

class RepoConfigController:
    class Signals(QObject):
        pass

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

        # setup UI
        self.ui = Ui_RepoConfigPage()
        self.widget = QWidget()
        self.ui.setupUi(self.widget)

        self.populate_lists()

        # create list move controller
        self.list_move = ListMoveController(
                self.ui.local_list, self.ui.to_remotes,
                self.ui.remote_list, self.ui.to_locals
        )

        # remove new and delete buttons for non-admins
        if not is_admin:
            self.ui.new_repo_button.hide()
            self.ui.delete_repo_button.hide()

        # signal connections
        self.ui.new_repo_button.clicked.connect(lambda _: self.create_remote_dialog())
        self.ui.delete_repo_button.clicked.connect(lambda _: self.delete_remote_dialog())
        self.ui.remote_list.itemSelectionChanged.connect(lambda: self.update_delete_button())
        self.ui.control_buttons.clicked.connect(lambda _: self.apply())

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
        remote_repos = None
        try:
            remote_repos = set(self.self_cmds.repos())
        except CommandError as ex:
            self.show_error(self.unknown_error(ex))
        if remote_repos:
            remote_repos -= local_repos
            self.ui.remote_list.addItems(remote_repos)

    def apply(self):
        local_delete = self.list_move.diff(ListMoveController.Direction.Right)
        if local_delete:
            ok = self.local_delete_dialog(local_delete)
            if ok:
                self.local_delete(local_delete)

        remote_clone = self.list_move.diff(ListMoveController.Direction.Left)
        if remote_clone:
            clone = CloneDialogController(self.widget)
            clone.signals.repo_paths_selected.connect(lambda repos: self.remote_clone(repos))
            clone.open()

    def discard(self):
        self.list_move.reset_diff()

    def create_remote_dialog(self):
        while True:
            remote_name, ok = QInputDialog.getText(
                    self.widget,
                    self.widget.tr('Create remote'),
                    self.widget.tr('Name of new remote:')
            )
            
            if ok:
                err = None
                if remote_name:
                    try:
                        self.repo_cmds.create(remote_name)
                    except RepoExists:
                        err = (
                                self.widget.tr('Repository exists'),
                                ' '.join((self.widget.tr('Repository with name'), remote_name, self.widget.tr('already exists')))
                        )
                    except InvalidRepoName:
                        err = (
                                self.widget.tr('Invalid repository name'),
                                ' '.join((remote_name, self.widget.tr('is not a valid repository name')))
                        )
                    except CommandError as ex:
                        err = self.unknown_error(ex)
                else:
                    err = (
                            self.widget.tr('Empty repository name'),
                            self.widget.tr('Repository name can not be empty')
                    )

                if err:
                    self.show_error(err)
                else:
                    self.ui.remote_list.addItem(QListWidgetItem(remote_name))
                    break
            else:
                # cancel
                break

    def delete_remote_dialog(self):
        remote_name = self.ui.remote_list.selectedItems()[0].text()
        ok = QMessageBox.question(
                self.widget,
                self.widget.tr('Remote repository deletion'),
                ' '.join((self.widget.tr('Remove remote repository'), remote_name))
        )
        if ok == QMessageBox.StandardButton.Yes:
            err = None
            try:
                self.repo_cmds.delete(remote_name)
            except RepoNotFound:
                err = (
                        self.widget.tr('Repository was not found'),
                        ' '.join((self.widget.tr('Repository'), remote_name, self.widget.tr('was not found on server')))
                )
            except CommandError:
                err = self.unknown_error(ex)
            if err:
                self.show_error(err)

    def local_delete_dialog(self, local_delete: set[str]):
        repo_text = self.bullet_list(local_delete)
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
                msg.append(self.bullet_list(not_deleted))
            if not_found:
                msg.append(self.widget.tr('Following repositories were not found:'))
                msg.append(self.bullet_list(not_found))
            self.show_error(self.widget.tr('Deletion error'), '\n'.join(msg))
        else:
            QMessageBox.information(
                    self.widget,
                    self.widget.tr('Success'),
                    self.widget.tr('Repositories were deleted successfully')
            )

    def remote_clone(self, repos: list['config.Repo']):
        not_cloned = set()
        for repo in repos:
            try:
                self.git_cloner.clone(repo)
                self.config.add_repo(repo)
            except GitCommandError as ex:
                self.show_error(ex)
                not_cloned.add(repo.name)
        if not_cloned:
            self.show_error((
                self.widget.tr('Cloning failed'),
                self.widget.tr('Failed to clone repositories:') + self.bullet_list(not_cloned)
            ))
        else:
            QMessageBox.information(
                    self.widget,
                    self.widget.tr('Success'),
                    self.widget.tr('Repositories were cloned successfully')
            )

    def update_delete_button(self):
        remote_selection = self.ui.remote_list.selectedItems()
        self.ui.delete_repo_button.setEnabled(bool(remote_selection))

    @staticmethod
    def bullet_list(repos: set[str]):
        return ''.join((f'\n  - {repo}' for repo in repos))

    def unknown_error(self, ex: CommandError):
        return (
                self.widget.tr('Unknown error'),
                ex.message
        )

    def show_error(self, err):
        QMessageBox.critical(
            self.widget,
            err[0],
            err[1]
        )
