import unittest
from nose.plugins.skip import SkipTest


class TestSimple(unittest.TestCase):
    """Specifically tests when inheriting from unittest.TestCase"""

    @classmethod
    def setupClass(cls):
        assert False

    def test_simple_fail(self):
        assert 1 == 0

    def test_simple_ok(self):
        assert 1 == 1

    def test_simple_skip(self):
        raise SkipTest()
