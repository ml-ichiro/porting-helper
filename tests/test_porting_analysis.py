from unittest import TestCase

from git import Repo
from os import path
import subprocess

from porting_analysis import PortingAnalysis

class TestPortingAnalysis(TestCase):
	repo_path = './tests/foo'

	@classmethod
	def setUpClass(klass):
		subprocess.call(['tar', 'xzf', './tests/foo.tar.gz', '-C', './tests'])

	@classmethod
	def tearDownClass(klass):
		subprocess.call(['rm', '-rf', './tests/foo'])

	def setUp(self):
		self.target = PortingAnalysis(TestPortingAnalysis.repo_path)

	def tearDown(self):
		pass

	def test_dir(self):
		self.assertEqual(
				self.target.dir(),
				path.abspath(TestPortingAnalysis.repo_path))

	def test_commits(self):
		l, r = self.target.commits()
		self.assertEqual(len(l), 4)
		self.assertEqual(len(r), 1)
		self.assertTrue(r[0][2])
		print('>>>> commits')
		for i in l:
			print(i.summary);
		print('<<<<')
		print('==== reverts')
		print(r[0])

	def test_commits_partial(self):
		l, r = self.target.commits(rev='HEAD~2..HEAD')
		self.assertEqual(len(l), 2)
		self.assertEqual(len(r), 1)
		self.assertFalse(r[0][2])

# vim: set tabstop=3 shiftwidth=3 :
