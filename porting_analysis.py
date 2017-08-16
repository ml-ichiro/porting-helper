from git import Repo
import re	# Regular Expression
import abc	# Abstruct Base Class

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

			keep = True
			for f in filters:
				keep &= f.action(c)

			if (keep):
				commit_list.append(c)

		results = [commit_list]
		for f in filters:
			results.append(f.get_results())

		return results

# vim: set shiftwidth=3 tabstop=3 :
