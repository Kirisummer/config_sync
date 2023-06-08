from git import Repo
from git.exc import GitCommandError, BadName

from .ssh import SSHCmdBits, SSHCreds

def get_repo_url(creds: 'SSHCreds', repo_name: str):
    return f'ssh://{creds.login}@{creds.host}:{creds.port}' \
           f'/~{creds.login}/repos/{repo_name}'

def get_ssh_cmd(cmd_bits: 'SSHCmdBits', creds: 'SSHCreds'):
    return (*cmd_bits.passwd_pipe, creds.password, *cmd_bits.ssh_opts)

def ignore_git_command_error(func):
    try:
        return func()
    except GitCommandError:
        pass

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
        ignore_git_command_error(lambda: self.repo.git.restore('--staged', '.'))
        ignore_git_command_error(lambda: self.repo.git.restore('.'))

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

    def fetch(self):
        self.discard_local()
        ignore_git_command_error(lambda: self.repo.git.checkout('HEAD', '--detach'))
        for branch in self.branches():
            self.repo.git.branch('-D', branch)
        with self.repo.git.custom_environment(GIT_SSH_COMMAND=' '.join(self.ssh_cmd)):
            self.repo.git.fetch('--all')
        for ref in self.refs():
            self.repo.git.checkout('--track', ref)

    def push(self, ref):
        with self.repo.git.custom_environment(GIT_SSH_COMMAND=' '.join(self.ssh_cmd)):
            self.repo.git.push(ref.split('/'))

    def branches(self):
        return [branch.name for branch in self.repo.branches]

    def refs(self):
        return [ref.name for ref in self.repo.remote().refs]

    def remote(self):
        return self.repo.remote().name

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
