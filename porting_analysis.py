from git import Repo, Commit
import subprocess
import re	# Regular Expression
import abc	# Abstruct Base Class

class CommitWithId():
	patchid = b''

	def __init__(self, commit):
		self.commit = commit
		self.patchid = self.set_patchid(commit.hexsha)

	def set_patchid(self, hexsha):
		command = 'git show ' + hexsha + '| git patch-id'
		outstr = subprocess.Popen(
				command,
				cwd=self.commit.repo.working_dir,
				stdout=subprocess.PIPE,
				shell=True
				).communicate()[0]
		return outstr.split()[0]

	def __getattr__(self, name):
		return getattr(self.commit, name)

class Filter(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def action(self, commit):
		return True

	@abc.abstractmethod
	def get_results(self):
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

class PortingAnalysis:
	repository = ''

	def __init__(self, repo='.'):
		self.repository = Repo(repo)

	def dir(self):
		return self.repository.working_dir

	def commits(self, rev='HEAD', paths='.', filters=[]):
		commit_list = []  # list of list(git.Commit, patchid)

		for c in self.repository.iter_commits(rev=rev, paths=paths):
			if (len(c.parents) > 1):
				continue  # skip merge commits

			c_id = CommitWithId(c)

			keep = True
			for f in filters:
				keep &= f.action(c_id)

			if (keep):
				commit_list.append(c_id)

		results = [commit_list]
		for f in filters:
			results.append(f.get_results())

		return results

# vim: set shiftwidth=3 tabstop=3 :
