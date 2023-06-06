from git import Repo
from git.exc import GitCommandError, BadName

from .ssh import SSHCmdBits, SSHCreds

def get_repo_url(creds: 'SSHCreds', repo_name: str):
    return f'ssh://{creds.login}@{creds.host}:{creds.port}' \
           f'/~{creds.login}/repos/{repo_name}'

def get_ssh_cmd(cmd_bits: 'SSHCmdBits', creds: 'SSHCreds'):
    return (*cmd_bits.passwd_pipe, creds.password, *cmd_bits.ssh_opts)

class GitRepo:
    def __init__(self,
                 repo: 'commit.Repo',
                 creds: SSHCreds,
                 cmd_bits: SSHCmdBits):
        self.repo = Repo(repo.path)
        self.repo_url = get_repo_url(creds, repo.name)
        self.ssh_cmd = get_ssh_cmd(cmd_bits, creds)

    @classmethod
    def get(cls, repo: 'commit.Repo', creds: SSHCreds):
        return cls(repo, creds, SSHCmdBits.get())

    def head(self):
        if self.repo.head.is_valid():
            return self.repo.head.commit.hexsha
        else:
            return None

    def revision_log(self, revision):
        try:
            commit = self.repo.rev_parse(revision)
        except BadName:
            return []
        log = [commit, *list(commit.iter_parents())]
        return map(lambda commit: (commit.hexsha, commit.summary), log)

    def local_changes(self):
        return map(lambda diff: diff.a_path, self.repo.index.diff(None))

    def commit_stat(self, revision):
        commit = self.repo.rev_parse(revision)
        return list(commit.stats.files), commit.message

    def discard_local(self):
        self.repo.git.restore('--staged', '.')
        self.repo.git.checkout('--', '.')

    def checkout(self, revision):
        self.discard_local()
        self.repo.git.checkout(revision)

    def diff(self, revision, file_path):
        # cut first three lines (diff command, index hashes, blob filenames)
        diff_lines = self.repo.git.show(
                '--color=never', '--pretty=tformat:',
                revision, file_path
        ).split('\n', 5)
        return diff_lines[-1]

    def branches(self):
        return list(branch.name for branch in self.repo.branches)

class GitCloner:
    def __init__(self,
                 cmd_bits: SSHCmdBits,
                 creds: SSHCreds):
        self.ssh_cmd = ' '.join(get_ssh_cmd(cmd_bits, creds))
        self.creds = creds

    @classmethod
    def get(cls, creds: SSHCreds):
        return cls(SSHCmdBits.get(), creds)

    def clone(self, repo: 'commit.Repo'):
        repo_url = get_repo_url(self.creds, repo.name)
        Repo.clone_from(
                repo_url,
                repo.path,
                env=dict(GIT_SSH_COMMAND=self.ssh_cmd)
        )
