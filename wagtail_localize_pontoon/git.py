import os.path
from contextlib import contextmanager

import pygit2
import toml


class Repository:
    def __init__(self, repo):
        self.repo = repo

    @classmethod
    def get_remote_callbacks(cls):
        keypair = pygit2.KeypairFromAgent("git")
        return pygit2.RemoteCallbacks(credentials=keypair)

    @classmethod
    def open(cls):
        REMOTE_URL = 'git@github.com:kaedroho/pontoon-test.git'
        LOCAL_DIR = '/home/vagrant/pontoon-test.git'

        if not os.path.isdir(LOCAL_DIR):
            print("Cloning repo from git...")

            pygit2.clone_repository(
                REMOTE_URL, LOCAL_DIR, bare=True,
                callbacks=self.get_remote_callbacks(),
            )

        return cls(pygit2.Repository(LOCAL_DIR))

    def reader(self):
        return RepositoryReader(self.repo)

    def writer(self):
        return RepositoryWriter(self.repo)

    def pull(self):
        self.repo.remotes[0].fetch(callbacks=self.get_remote_callbacks())
        new_head = self.repo.lookup_reference('refs/remotes/origin/master')
        return RepositoryMerger(self.repo, new_head)

    def try_push(self):
        self.repo.remotes[0].push(['refs/heads/master'], callbacks=self.get_remote_callbacks())


class RepositoryMerger:
    def __init__(self, repo, new_head):
        self.repo = repo
        self.new_head = new_head

    def changed_files(self):
        """
        For each file that has changed, yields a three-tuple containing the filename, old content and new content
        """
        old_index = pygit2.Index()
        new_index = pygit2.Index()
        old_index.read_tree(self.repo.get(self.repo.head.target).tree)
        new_index.read_tree(self.repo.get(self.new_head.target).tree)

        for patch in self.repo.diff(self.repo.head, self.new_head):
            old_file_oid = old_index[patch.delta.old_file.path].oid
            new_file_oid = new_index[patch.delta.new_file.path].oid
            old_file = self.repo.get(old_file_oid)
            new_file = self.repo.get(new_file_oid)
            yield patch.delta.new_file.path, old_file.data, new_file.data

    def commit(self):
        """
        Updates the local master branch to match the remote
        """
        self.repo.head.set_target(self.new_head.target)


class RepositoryReader:
    def __init__(self, repo):
        self.repo = repo
        self.index = pygit2.Index()
        self.last_commit = self.repo.head.target
        self.index.read_tree(self.repo.get(self.last_commit).tree)

    def read_file(self, filename):
        oid = self.index[filename].oid
        return self.repo.get(oid).data


class RepositoryWriter:
    def __init__(self, repo):
        self.repo = repo
        self.index = pygit2.Index()

    def has_changes(self):
        """
        Returns True if the contents of this writer is different to the repo's current HEAD
        """
        tree = self.repo.get(self.index.write_tree(self.repo))
        diff = tree.diff_to_tree(self.repo.get(self.repo.head.target).tree)
        return bool(diff)

    def write_file(self, filename, contents):
        """
        Inserts a file into this writer
        """
        blob = self.repo.create_blob(contents)
        self.index.add(pygit2.IndexEntry(filename, blob, pygit2.GIT_FILEMODE_BLOB))

    def write_config(self, languages, paths):
        self.write_file('l10n.toml', toml.dumps({
            'locales': languages,
            'paths': [
                {
                    'reference': str(source_path),
                    'l10n': str(locale_path),
                }
                for source_path, locale_path in paths
            ]
        }))

    def commit(self, message):
        """
        Creates a new commit with the contents of this writer
        """
        tree = self.index.write_tree(self.repo)

        sig = pygit2.Signature('Wagtail Localize', 'wagtail_localize_pontoon@wagtail.io')
        self.repo.create_commit('refs/heads/master', sig, sig, message, tree, [self.repo.head.target])
