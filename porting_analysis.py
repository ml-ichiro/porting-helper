from git import Repo
import re

targets = (
	'drivers/gpu/drm',
	'include/drm',
)


class PortingAnalysis:
	repository = ''

	def __init__(self, repo='.'):
		self.repository = Repo(repo)

	def dir(self):
		return self.repository.working_dir

	def commits(self, rev='HEAD', paths='.'):
		revert_commit_expr = re.compile(
				"This reverts\n? '?commit ([0-9a-f]*)", re.MULTILINE)

		def get_victim(message):
			matched = revert_commit_expr.search(message)

			if (matched is None):
				return '--'

			return matched.group(1)

		commit_list = []  # list of git.Commit
		revert_list = []  # list of list(revert, original, found)

		for c in self.repository.iter_commits(rev=rev, paths=paths):
			if (len(c.parents) > 1):
				continue  # skip merge commits

			commit_list.append(c)

			if (c.summary.startswith('Revert "')):
				victim = get_victim(c.message)
				revert_list.append([c.hexsha, victim, False])

			for r in revert_list:
				if (c.hexsha.startswith(r[1])):
					r[2] = True

		return commit_list, revert_list

# vim: set shiftwidth=3 tabstop=3 :
