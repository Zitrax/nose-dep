from nosedep import depends
from nose.tools import assert_true, assert_false
import unittest


class TestNoseDecoratedTestCaseParent(unittest.TestCase):
    did_setup_class = False
    did_teardown_class = False

    @classmethod
    def reset(cls):
        cls.did_setup_class = False
        cls.did_teardown_class = False

    def __init__(self, methodName='runTest'):
        super(TestNoseDecoratedTestCaseParent, self).__init__(methodName)
        self.did_setup = False
        self.did_teardown = False

    @classmethod
    def setup_class(cls):
        cls.did_setup_class = True
        # Would be better to reset this externally
        cls.did_teardown_class = False

    @classmethod
    def teardown_class(cls):
        cls.did_teardown_class = True

    def setUp(self):
        self.did_setup = True

    def tearDown(self):
        self.did_teardown = True


class TestNoseDecoratedTestCaseChild(TestNoseDecoratedTestCaseParent):
    def test_cdt_a(self):
        assert_true(self.did_setup)
        assert_true(self.did_setup_class)
        assert_false(self.did_teardown)
        assert_false(self.did_teardown_class)

    def test_cdt_b(self):
        pass

    @depends(before='test_cdt_b')
    def test_cdt_c(self):
        pass
