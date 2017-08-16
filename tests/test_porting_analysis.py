from unittest import TestCase

from git import Repo
from os import path
import subprocess

from porting_analysis import PortingAnalysis, RevertFilter

class TestPortingAnalysis(TestCase):
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
		self.target = PortingAnalysis(TestPortingAnalysis.repo_path)

	def tearDown(self):
		pass

	def test_dir(self):
		self.assertEqual(
				self.target.dir(),
				path.abspath(TestPortingAnalysis.repo_path))

	def test_commits(self):
		l = self.target.commits()
		self.assertEqual(len(l), 1)
		commits = l[0];
		self.assertEqual(len(commits), 5)
		print('>>>> commits')
		for c in commits:
			print(c.summary);
		print('<<<<')

	def test_commits_partial(self):
		l = self.target.commits(rev='HEAD~2..HEAD')
		self.assertEqual(len(l), 1)
		commits = l[0];
		self.assertEqual(len(commits), 2)

	def test_commits_branch(self):
		l = self.target.commits(rev='dev_b~3..dev_b')
		self.assertEqual(len(l), 1)
		commits = l[0];
		self.assertEqual(len(commits), 3)

	def test_filter_revert(self):
		l = self.target.commits(filters=[RevertFilter()])
		self.assertEqual(len(l), 2)
		reverts = l[1];
		self.assertEqual(len(reverts), 1)
		print('>>>> commits')
		for c in reverts:
			print(c[0], ' ', c[1], ' ', c[2]);
		print('<<<<')
		self.assertEqual(reverts[0][2], True)

# vim: set tabstop=3 shiftwidth=3 :
