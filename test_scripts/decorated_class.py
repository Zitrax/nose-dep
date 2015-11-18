import unittest

from nosedep import depends


def test_decorated_class_dep():
    assert 1


@depends(after=test_decorated_class_dep)
class TestSimpleDecoratedClass(unittest.TestCase):
    def test_decorated_class_internal(self):
        assert 1
