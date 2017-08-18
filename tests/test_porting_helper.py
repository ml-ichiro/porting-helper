from unittest import TestCase

from git import Repo
from os import path
import subprocess

from porting_helper import *


class TestPortingHelper(TestCase):
    repo_path = './tests/foo'
    message_buf = []

    @classmethod
    def setUpClass(klass):
        subprocess.call(['tar', 'xzf', './tests/foo.tar.gz', '-C', './tests'])
        pass

    @classmethod
    def tearDownClass(klass):
        print()
        for l in TestPortingHelper.message_buf:
            print(l)
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
        commits = self.target.commits()
        self.assertEqual(len(commits), 5)

        self.message_buf.append('>>>> commits')
        for c in commits:
            self.message_buf.append('%s %s' % (c.patchid, c.summary))
        self.message_buf.append('<<<<')

    def test_commits_partial(self):
        commits = self.target.commits(rev='HEAD~2..HEAD')
        self.assertEqual(len(commits), 2)

    def test_commits_branch(self):
        commits = self.target.commits(rev='dev_b~3..dev_b')
        self.assertEqual(len(commits), 3)

    def test_commits_paths_file(self):
        commits = self.target.commits(rev='dev_b')
        self.assertEqual(len(commits), 7)  # all to the beginning
        commits = self.target.commits(rev='dev_b', paths=['b.txt'])
        self.assertEqual(len(commits), 2)  # only about 'b.txt'

    def test_commits_paths_none(self):
        commits = self.target.commits(rev='dev_b', paths=None)
        self.assertEqual(len(commits), 7)  # All

    def test_commits_paths_dot(self):
        commits = self.target.commits(rev='dev_b', paths=['.'])
        self.assertEqual(len(commits), 7)  # only about 'b.txt'

    def test_commits_paths_dot2(self):
        commits = self.target.commits(rev='dev_b', paths='.')
        self.assertEqual(len(commits), 7)  # only about 'b.txt'

    def test_commits_paths_nullstr(self):
        commits = self.target.commits(rev='dev_b', paths='')
        self.assertEqual(len(commits), 7)  # only about 'b.txt'

    def test_filter_revert(self):
        f = RevertFilter()
        commits = self.target.commits(filters=[f])
        reverts = f.get_results()
        self.assertEqual(len(reverts), 1)
        self.assertEqual(reverts[0][2], True)

        self.message_buf.append('>>>> reverts')
        for c in reverts:
            self.message_buf.append('%s %s %s' % tuple(c))
        self.message_buf.append('<<<<')

    def test_filter_patchid(self):
        commits = self.target.commits(rev='dev_b~3..dev_b')
        pif = PatchIdFilter(commits)
        ids = pif.get_results()
        self.assertEqual(len(ids), 3)

        self.message_buf.append('>>>> patch ids')
        for i in ids:
            self.message_buf.append(i)
        self.message_buf.append('<<<<')

        commits = self.target.commits(filters=[pif])
        self.assertEqual(len(commits), 4)  # One less than all

    def test_filter_summary(self):
        commits = self.target.commits(rev='dev_b~3..dev_b')
        pif = SummaryFilter(commits)
        ids = pif.get_results()
        self.assertEqual(len(ids), 3)

        self.message_buf.append('>>>> summary lines')
        for i in ids:
            self.message_buf.append(i)
        self.message_buf.append('<<<<')

        commits = self.target.commits(filters=[pif])
        self.assertEqual(len(commits), 4)  # One less than all

# vim: set shiftwidth=4 tabstop=99 :
