'''
Provides PortingHelper class and filtering classes
to get list of commits in user specified criteria.
'''

from typing import List, Any, Union

from git import Repo, Commit
from gitdb.exc import BadName
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
    PATCH_ID_EMPTY = '0' * 40

    def __init__(self, commit):
        self.commit = commit
        if commit.stats.total['files'] > 0:
            self.patchid = self.set_patchid(commit.hexsha)
        else:
            self.patchid = CommitWithId.PATCH_ID_EMPTY

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
    '''
    Abstract class of commit filters
    '''

    @abc.abstractmethod
    def action(self, commit: CommitWithId) -> bool:
        '''
        :param commit: CommitWithId instance, almost same as gitpython's Commit
        :return: True to keep the commit, False to drop it
        '''
        return True

    @abc.abstractmethod
    def get_results(self) -> List[Any]:
        '''
        :return: Filter's internal array (contents varies by Filters)
        '''
        return []


class RevertFilter(Filter):
    '''
    Find revert pairs
    '''
    _REVERT_COMMIT_EXPR = re.compile(
            "This reverts\n? '?commit ([0-9a-f]*)", re.MULTILINE)

    def __init__(self):
        self.revert_list = []

    def get_reverted(self, message):
        matched = self._REVERT_COMMIT_EXPR.search(message)

        if matched is None:
            return '--'

        return matched.group(1)

    def action(self, commit):
        '''
        :param commit: CommitWithId instance, almost same as gitpython's Commit
        :return: True (this filter doesn't drop any commit)
        '''
        if commit.summary.startswith('Revert "'):
            reverted = self.get_reverted(commit.message)
            self.revert_list.append([commit.hexsha, reverted, False])

        for r in self.revert_list:
            if commit.hexsha.startswith(r[1]):
                r[2] = True
                break

        return True

    def get_results(self):
        '''
        :return: List of triplet,
            (revert hash, reverted hash, "is included" flag)
            The flag "is included" is True when the reverted commit is
            found in the examined series.
        '''
        return self.revert_list


class PatchIdFilter(Filter):
    '''
    Drop commit of a series if the patch-id is found in
    a set of IDs created from another series
    '''

    def __init__(self, commits: List[CommitWithId]):
        '''
        :param commits: List of gitpython Commit instances
        '''
        self.patchid_set = set([c.patchid for c in commits])
        self.patchid_list = [[c] for c in commits]

    def action(self, commit):
        '''
        :param commit: CommitWithId instance, almost same as gitpython's Commit
        :return: False if given patch-id is found in the set
        '''
        if commit.patchid in self.patchid_set:
            for item in self.patchid_list:
                if item[0].patchid == commit.patchid:
                    item.append(commit.hexsha)
                    break
            return False

        return True

    def get_results(self):
        '''
        :return: List of patch-ids
        '''
        return self.patchid_list


class SummaryFilter(Filter):
    '''
    Drop commit of a series if the sammary line is same as
    a commit in another series
    '''

    def __init__(self, commits: List[CommitWithId]):
        '''
        :param commits: List of gitpython Commit instances
        '''
        self.summary_set = set([c.summary for c in commits])
        self.summary_list = [[c] for c in commits]  # List of length-1 lists

    def action(self, commit):
        '''
        :param commit: CommitWithId instance, almost same as gitpython's Commit
        :return: False if given summary line is found in the set
        '''
        if commit.summary in self.summary_set:
            for item in self.summary_list:
                if item[0].summary == commit.summary:
                    item.append(commit.hexsha)
                    break
            return False

        return True

    def get_results(self):
        '''
        :return: List of summary lines
        '''
        return self.summary_list


class PortingHelper:
    '''
    Helper class to get filtered commit list from gitpython.Repo
    '''

    def __init__(self, repo: str = '.'):
        '''
        :param repo: Git repository path
        '''
        self.repository = Repo(repo)

    def dir(self) -> str:
        '''
        :return: Current Git repository path
        '''
        return self.repository.working_dir

    def commits(self, rev: str = 'HEAD', paths: Union[str, List[str]] = '',
                filters: List[Filter] = []) -> List[CommitWithId]:
        '''
        :param rev: Git revision selection string, typically a range of commits
        :param paths: Target dir/file path or list of paths
        :param filters: List of Filter instances
        :return: List of commits in reverse chronological order
        '''
        commit_list = []  # list of CommitWithId

        for c in self.repository.iter_commits(rev=rev, paths=paths):
            if len(c.parents) > 1:
                continue  # skip merge commits

            c_id = CommitWithId(c)

            keep = True
            for f in filters:
                keep &= f.action(c_id)
                if not keep:
                    break

            if keep:
                commit_list.append(c_id)

        return commit_list

    def commits_from_hashes(self, hashes: List[str] = []) -> List[CommitWithId]:
        '''
        :param hashes: List of Git commit IDs
        '''
        commit_list = []  # list of CommitWithId

        for h in hashes:
            try:
                c = self.repository.commit(h)
            except BadName as e:
                continue

            if len(c.parents) > 1:
                continue

            c_id = CommitWithId(c)
            commit_list.append(c_id)

        return commit_list

# vim: set shiftwidth=4 tabstop=99 :
