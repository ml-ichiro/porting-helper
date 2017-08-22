from typing import List, Any, Union

from git import Repo, Commit
import subprocess
import re    # Regular Expression
import abc   # Abstruct Base Class

__all__ = [
    'PortingHelper',
    'Filter',
    'RevertFilter',
    'PatchIdFilter',
    'SummaryFilter',
]


class CommitWithId():
    patchid = b''

    def __init__(self, commit):
        self.commit = commit
        self.patchid = self.set_patchid(commit.hexsha)

    def set_patchid(self, hexsha):
        command = 'git show ' + hexsha + '| git patch-id'
        outstr = subprocess.Popen(command,
                                  cwd=self.commit.repo.working_dir,
                                  stdout=subprocess.PIPE,
                                  shell=True
                                  ).communicate()[0]
        return outstr.split()[0]

    def __getattr__(self, name):
        return getattr(self.commit, name)


class Filter(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def action(self, commit: CommitWithId) -> bool:
        return True

    @abc.abstractmethod
    def get_results(self) -> List[Any]:
        return []


class RevertFilter(Filter):
    revert_list = []
    revert_commit_expr = re.compile(
            "This reverts\n? '?commit ([0-9a-f]*)", re.MULTILINE)

    def get_reverted(self, message):
        matched = self.revert_commit_expr.search(message)

        if (matched is None):
            return '--'

        return matched.group(1)

    def action(self, commit):
        if (commit.summary.startswith('Revert "')):
            reverted = self.get_reverted(commit.message)
            self.revert_list.append([commit.hexsha, reverted, False])

        for r in self.revert_list:
            if (commit.hexsha.startswith(r[1])):
                r[2] = True

        return True

    def get_results(self):
        return self.revert_list


class PatchIdFilter(Filter):
    patchid_set = set()

    def __init__(self, commits: List[CommitWithId]):
        for c in commits:
            self.patchid_set.add(c.patchid)

    def action(self, commit):
        if (commit.patchid in self.patchid_set):
            return False

        return True

    def get_results(self):
        l = []

        for i in self.patchid_set:
            l.append(i)

        return l


class SummaryFilter(Filter):
    summary_set = set()

    def __init__(self, commits: List[CommitWithId]):
        for c in commits:
            self.summary_set.add(c.summary)

    def action(self, commit):
        if (commit.summary in self.summary_set):
            return False

        return True

    def get_results(self):
        l = []

        for i in self.summary_set:
            l.append(i)

        return l


class PortingHelper:
    repository = ''

    def __init__(self, repo: str = '.'):
        self.repository = Repo(repo)

    def dir(self) -> str:
        return self.repository.working_dir

    def commits(self, rev: str = 'HEAD', paths: Union[str, List[str]] = '',
                filters: List[Filter] = []) -> List[CommitWithId]:
        commit_list = []  # list of CommitWithId

        for c in self.repository.iter_commits(rev=rev, paths=paths):
            if (len(c.parents) > 1):
                continue  # skip merge commits

            c_id = CommitWithId(c)

            keep = True
            for f in filters:
                keep &= f.action(c_id)

            if (keep):
                commit_list.append(c_id)

        return commit_list

# vim: set shiftwidth=4 tabstop=99 :
