from dataclasses import dataclass, field

from git import Repo

@dataclass(frozen=True)
class GitRepo:
    repo: 'config.Repo'
    ssh: 'api.ssh.SSH'
    git: Repo = field(init=False)

    def __post_init__(self):
        super().__setattr__('git', Repo(self.repo.path))

    def head(self):
        return self.git.head.commit.hexsha

    def revision_log(self, revision):
        commit = self.git.rev_parse(revision)
        log = [commit, *list(commit.iter_parents())]
        return map(lambda commit: (commit.hexsha, commit.summary), log)

    def local_changes(self):
        return map(lambda diff: diff.a_path, self.git.index.diff(None))

    def discard_local(self, revision):
        self.git.git.restore('--staged', '.')
        self.git.git.checkout('--', '.')

    def checkout(self, revision):
        self.discard_local()
        self.git.git.checkout(revision)

