import os
import unittest
from nose.plugins import PluginTester
from nose.plugins.xunit import Xunit
from nose.tools import assert_in
from nosedep import NoseDep


class NoseDepPluginTester(PluginTester, unittest.TestCase):
    activate = '--with-nosedep'
    args = ['-v']
    plugins = [NoseDep()]

    # This is a bit odd. If using the absolute path on Windows
    # it tries to import module 'C' due to the ':' , if only relative path
    # it splits on the '.' before the file extension.
    # So I only got it to work with a relative path appended with a ':'.
    suitepath = None

    def makeSuite(self):
        raise Exception("Should not be used currently")

    def check(self, expect):
        results = len(expect)
        for line in self.output:
            if expect:
                self.assertEqual(line.strip(), expect.pop(0))
        # Verify that we ran the expected number of tests
        assert_in("Ran {} test{} in".format(results, 's' if results > 1 else ''),
                  str(self.output))


class TestUndecoratedFunctional(NoseDepPluginTester):
    suitepath = "test_scripts/undecorated_functional_tests.py:"

    def runTest(self):
        self.check(['test_scripts.undecorated_functional_tests.test_x ... ok',
                    'test_scripts.undecorated_functional_tests.test_y ... ERROR'])


class TestUndecoratedFunctionalXunit(NoseDepPluginTester):
    # Initially there was a bug causing Xunit to fail in
    # combination with nosedep. This test verifies that it works.
    args = ['-v', '--with-xunit']
    plugins = [NoseDep(), Xunit()]
    suitepath = "test_scripts/undecorated_functional_tests.py:"

    def setUp(self):
        if os.path.isfile('nosetests.xml'):
            os.remove('nosetests.xml')
        super(TestUndecoratedFunctionalXunit, self).setUp()

    def tearDown(self):
        with open('nosetests.xml') as xml:
            assert_in('tests="2"', xml.read())
        super(TestUndecoratedFunctionalXunit, self).tearDown()

    def runTest(self):
        self.check(['test_scripts.undecorated_functional_tests.test_x ... ok',
                    'test_scripts.undecorated_functional_tests.test_y ... ERROR'])


class TestDecoratedFunctionalAll(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_tests.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_f ... ok',
                    'test_scripts.decorated_functional_tests.test_b ... ok',
                    'test_scripts.decorated_functional_tests.test_e ... ok',
                    'test_scripts.decorated_functional_tests.test_a ... ok',
                    'test_scripts.decorated_functional_tests.test_c ... ok',
                    'test_scripts.decorated_functional_tests.test_d ... ok'])


class TestDecoratedFunctionalFunc(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_func.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_func.test_dff_b ... ok',
                    'test_scripts.decorated_functional_func.test_dff_a ... ok',
                    'test_scripts.decorated_functional_func.test_dff_c ... ok'])


class TestDecoratedFunctionalMult(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_mult.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_mult.test_dfm_b ... ok',
                    'test_scripts.decorated_functional_mult.test_dfm_c ... ok',
                    'test_scripts.decorated_functional_mult.test_dfm_a ... ok'])


class TestDecoratedFunctionalSpecificDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_tests.py:test_d"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_b ... ok',
                    'test_scripts.decorated_functional_tests.test_a ... ok',
                    'test_scripts.decorated_functional_tests.test_d ... ok'])


class TestDecoratedFunctionalSpecificNoDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_tests.py:test_f"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_f ... ok'])


class TestUndecoratedMethod(NoseDepPluginTester):
    suitepath = "test_scripts/undecorated_method_tests.py:"

    def runTest(self):
        self.check(['test_scripts.undecorated_method_tests.TestNoseUndecoratedMethod.test_c_a ... ok',
                    'test_scripts.undecorated_method_tests.TestNoseUndecoratedMethod.test_c_b ... ok'])


class TestDecoratedMethod(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_tests.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_a ... ok',
                    'test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_c ... ok',
                    'test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_b ... ok'])


class TestDecoratedMethodSpecificNoDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_tests.py:TestNoseDecoratedMethod.test_cd_a"

    def runTest(self):
        self.check(['test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_a ... ok'])


class TestDecoratedMethodSpecificDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_tests.py:TestNoseDecoratedMethod.test_cd_b"

    def runTest(self):
        self.check(['test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_c ... ok',
                    'test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_b ... ok'])


if __name__ == '__main__':
    unittest.main()


# To test:
# * Multiple specifiers
# * Test both with file and __main__ specifying prefix
#   In the tested application use of __main__. tests all tests while filename prefix works.

# FIXME: Dependencies are global and not qualified. Would probably be best if
#        it contained unique qualifiers. (now we can't use the same test name in different files)
