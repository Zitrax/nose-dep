import unittest
from nose.plugins import PluginTester
from nose.tools import assert_true, assert_false
from nosedep import depends, NoseDep


@depends(after='test_b')
def test_a():
    assert_true(True)


def test_b():
    assert_true(True)


@depends(after='test_b')
def test_c():
    assert_true(True)


@depends(after='test_a')
def test_d():
    assert_true(True)


@depends(before='test_c')
def test_e():
    assert_true(True)


def test_f():
    pass


class TestNoseDep(object):
    did_setup_class = False
    did_teardown_class = False

    def __init__(self):
        self.did_setup = False
        self.did_teardown = False

    @classmethod
    def setup_class(cls):
        #import traceback
        #traceback.print_stack()
        cls.did_setup_class = True

    @classmethod
    def teardown_class(cls):
        cls.did_teardown_class = True

    def setup(self):
        self.did_setup = True

    def teardown(self):
        self.did_teardown = True

    def test_c_a(self):
        assert_true(self.did_setup)
        assert_true(self.did_setup_class)
        assert_false(self.did_teardown)
        assert_false(self.did_teardown_class)

    def test_c_b(self):
        pass

class TestFancyOutputter(PluginTester, unittest.TestCase):
    activate = '--with-nosedep'  # enables the plugin
    plugins = [NoseDep()]
    args = []
    env = {}

    def test_fancy_output(self):
        assert "FANCY FANCY FANCY" in self.output, ("got: %s" % self.output)

    def makeSuite(self):
        class TC(unittest.TestCase):
            def runTest(self):
                raise ValueError("I hate fancy stuff")
        return [TC('runTest')]

if __name__ == '__main__':
    # Temporary for force testing using the plugin
    #import nose
    #from nosedep import NoseDep
    #nose.main(defaultTest=__name__, addplugins=[NoseDep()])
    unittest.main()


# To test:
# * No specifier
# * Specifier for each functional test
# * Specifier for method tests
# * Multiple specifiers
# * Make sure a test that is not part of any dependency chain is tested
# * Test both with file and __main__ specifying prefix
# * Verify that setup/teardown is run both for func and method tests
# * Verify that each test only run a single time
