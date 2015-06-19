import unittest
import persist
import shutil
import tempfile
import os.path


class PersistTests(unittest.TestCase):

    def setUp(self):
        self.tempdir = tempfile.mkdtemp(prefix="andrey_persist_tests")
        if self.tempdir is None:
            raise RuntimeError("could not make temp dir")

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_msgpack_save_restore(self):
        fn = os.path.join(self.tempdir, 'msgpack_save_restore.mpack')

        first_markov = persist.PersistedMarkov(2, 3)
        first_markov.teach("I sell propane & propane accessories.")
        first_markov.save(fn)
        self.assertFalse(os.path.exists(fn + '.bak'))
        first_markov.save(fn)
        self.assertTrue(os.path.exists(fn + '.bak'))

        restored_markov = persist.PersistedMarkov.restore(fn)
        self.assertEquals(restored_markov.choose("Do you only sell propane my friend?"), "& propane accessories.")

    def test_restore_nosuchfile_no_create_parameters(self):
        fn = os.path.join(self.tempdir, 'doesnotexist.mpack')
        self.assertRaises(persist.NoSuchFileError, persist.PersistedMarkov.restore, fn)

    def test_restore_nosuchfile_default_options(self):
        fn = os.path.join(self.tempdir, 'doesnotexist2.mpack')
        m = persist.PersistedMarkov.restore(fn, 1, 1)
        m.teach("HELLO WORLD")
        self.assertEquals(m.choose("HELLO"), "WORLD")