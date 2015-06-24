import unittest
from nose.plugins import PluginTester
from nosedep import NoseDep
from test_scripts.decorated_method_tests import TestNoseDecoratedMethod


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
        for line in self.output:
            if expect:
                self.assertEqual(line.strip(), expect.pop(0))


class TestUndecoratedFunctional(NoseDepPluginTester):
    suitepath = "test_scripts/undecorated_functional_tests.py:"

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
# * No specifier
# * Specifier for each functional test
# * Specifier for method tests
# * Multiple specifiers
# * Make sure a test that is not part of any dependency chain is tested
# * Test both with file and __main__ specifying prefix
# * Verify that setup/teardown is run both for func and method tests
# * Verify that each test only run a single time

# FIXME: Dependencies are global and not qualified. Would probably be best if
#        it contained unique qualifiers. (now we can't use the same test name in different files)
