from unittest import TestCase

from git import Repo
from os import path
import subprocess

from porting_helper import PortingHelper, RevertFilter, PatchIdFilter

class TestPortingHelper(TestCase):
	repo_path = './tests/foo'

	@classmethod
	def setUpClass(klass):
		subprocess.call(['tar', 'xzf', './tests/foo.tar.gz', '-C', './tests'])
		pass

	@classmethod
	def tearDownClass(klass):
		subprocess.call(['rm', '-rf', './tests/foo'])
		pass

	def setUp(self):
		self.target = PortingHelper(TestPortingHelper.repo_path)

	def tearDown(self):
		pass

	def test_dir(self):
		self.assertEqual(
				self.target.dir(),
				path.abspath(TestPortingHelper.repo_path))

	def test_commits(self):
		l = self.target.commits()
		self.assertEqual(len(l), 1)
		commits = l[0]
		self.assertEqual(len(commits), 5)
		print('>>>> commits')
		for c in commits:
			print(c.summary, c.patchid)
		print('<<<<')

	def test_commits_partial(self):
		l = self.target.commits(rev='HEAD~2..HEAD')
		self.assertEqual(len(l), 1)
		commits = l[0]
		self.assertEqual(len(commits), 2)

	def test_commits_branch(self):
		l = self.target.commits(rev='dev_b~3..dev_b')
		self.assertEqual(len(l), 1)
		commits = l[0]
		self.assertEqual(len(commits), 3)

	def test_commits_paths(self):
		commits = self.target.commits(rev='dev_b')[0]
		self.assertEqual(len(commits), 7) # all to the beginning
		commits = self.target.commits(rev='dev_b', paths=['b.txt'])[0]
		self.assertEqual(len(commits), 2) # only about 'b.txt'

	def test_filter_revert(self):
		l = self.target.commits(filters=[RevertFilter()])
		self.assertEqual(len(l), 2)
		reverts = l[1]
		self.assertEqual(len(reverts), 1)
		print('>>>> reverts')
		for c in reverts:
			print(c[0], ' ', c[1], ' ', c[2])
		print('<<<<')
		self.assertEqual(reverts[0][2], True)

	def test_filter_patchid(self):
		l = self.target.commits(rev='dev_b~3..dev_b')
		pif = PatchIdFilter(l[0])
		ids = pif.get_results()
		self.assertEqual(len(ids), 3)
		print('>>>> patch ids')
		for i in ids:
			print(i)
		print('<<<<')

		l = self.target.commits(filters=[pif])
		self.assertEqual(len(l), 2)
		commits = l[0]
		ids = l[1]
		self.assertEqual(len(ids), 3)
		self.assertEqual(len(commits), 4) # One less than all

# vim: set tabstop=3 shiftwidth=3 :
