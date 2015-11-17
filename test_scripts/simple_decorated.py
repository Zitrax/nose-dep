import unittest

from nosedep import depends


class TestSimpleDecorated(unittest.TestCase):
    """Specifically tests when inheriting from unittest.TestCase"""
    @depends(after='test_simple_decorated_ok')
    def test_simple_decorated_fail(self):
        assert 1 == 0

    def test_simple_decorated_ok(self):
        assert 1 == 1

    @depends(after='test_simple_decorated_fail')
    def test_simple_decorated_skip(self):
        assert 1 == 1
