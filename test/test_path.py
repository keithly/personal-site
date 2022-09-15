import unittest

from test import path


class PathTest(unittest.TestCase):
    def test_temppath(self):
        self.assertTrue(path.temppath())
