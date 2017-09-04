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

    def test_commits_repeat(self):
        commits = self.target.commits()
        self.assertEqual(len(commits), 5)
        commits = self.target.commits()
        self.assertEqual(len(commits), 5)

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

    def test_commits_from_hashes(self):
        h = []
        with open('./tests/hash.txt') as f:
            for l in f:
                h.append(l.strip())
        commits = self.target.commits_from_hashes(hashes=h)
        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].summary, 'jane')
        self.assertEqual(commits[1].summary, 'Add Jane\'s family name')

    def test_commits_from_file_wronghash(self):
        h = []
        with open('./tests/hash_wrong.txt') as f:
            for l in f:
                h.append(l.strip())
        commits = self.target.commits_from_hashes(hashes=h)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].summary, 'jane')

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
        f = PatchIdFilter(commits)
        ids = f.get_results()
        self.assertEqual(len(ids), 3)
        [self.assertEqual(len(i), 1) for i in ids]

        commits = self.target.commits(filters=[f])
        self.assertEqual(len(commits), 4)  # One less than all
        ids = f.get_results()
        self.assertEqual(len(ids), 3)
        self.assertEqual(len(ids[0]), 1)  # Patch-Id '373167d...' has no match
        self.assertEqual(len(ids[1]), 2)  # Patch-Id '89958ac...' has a match "Add Jane's family name"

        self.message_buf.append('>>>> patch ids')
        for i in ids:
            self.message_buf.append(i[0].patchid)
            if len(i) > 1:
                self.message_buf.append('-> ' + i[1])
        self.message_buf.append('<<<<')

    def test_filter_patchid_repeat(self):
        commits = self.target.commits(rev='dev_b~3..dev_b')
        f = PatchIdFilter(commits)
        self.assertEqual(len(f.get_results()), 3)
        f = PatchIdFilter(commits)
        self.assertEqual(len(f.get_results()), 3)

    def test_filter_summary(self):
        commits = self.target.commits(rev='dev_b~3..dev_b')
        f = SummaryFilter(commits)
        ids = f.get_results()
        self.assertEqual(len(ids), 3)

        self.message_buf.append('>>>> summary lines')
        for i in ids:
            self.message_buf.append(i)
        self.message_buf.append('<<<<')

        commits = self.target.commits(filters=[f])
        self.assertEqual(len(commits), 4)  # One less than all

# vim: set shiftwidth=4 tabstop=99 :
