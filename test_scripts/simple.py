import unittest


class TestSimple(unittest.TestCase):
    """Specifically tests when inheriting from unittest.TestCase"""
    def test_simple_fail(self):
        assert 1 == 0

    def test_simple_ok(self):
        assert 1 == 1
