import os
import unittest

from nose.plugins import PluginTester
from nose.plugins.skip import Skip
from nose.plugins.xunit import Xunit
from nose.tools import assert_in, eq_

try:
    from nose.tools import assert_raises_regex
except ImportError:
    # For python 2.7
    from nose.tools import assert_raises_regexp as assert_raises_regex
from nosedep import NoseDep, depends


class NoseDepPluginTester(PluginTester, unittest.TestCase):
    activate = '--with-nosedep'
    args = ['-v']
    plugins = [NoseDep(), Skip()]

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
                self.assertEqual(expect.pop(0), line.strip())
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


class TestDecoratedClass(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_class.py"

    def setUp(self):
        try:
            super(TestDecoratedClass, self).setUp()
        except ValueError as e:
            eq_(str(e), "depends decorator can only be used on functions or methods")


class TestSimple(NoseDepPluginTester):
    suitepath = "test_scripts/simple.py"

    def runTest(self):
        self.check(['test_simple_fail (test_scripts.simple.TestSimple) ... FAIL',
                    'test_simple_ok (test_scripts.simple.TestSimple) ... ok',
                    'test_simple_skip (test_scripts.simple.TestSimple) ... SKIP'])


class TestSimpleDecorated(NoseDepPluginTester):
    suitepath = "test_scripts/simple_decorated.py"

    def runTest(self):
        self.check(['test_simple_decorated_ok (test_scripts.simple_decorated.TestSimpleDecorated) ... ok',
                    'test_simple_decorated_fail (test_scripts.simple_decorated.TestSimpleDecorated) ... FAIL',
                    'test_simple_decorated_skip (test_scripts.simple_decorated.TestSimpleDecorated) ... SKIP:'
                    ' Required test \'test_simple_decorated_fail\' FAILED'])


class TestSimpleColon(NoseDepPluginTester):
    suitepath = "test_scripts/simple.py:"

    def runTest(self):
        self.check(['test_simple_fail (test_scripts.simple.TestSimple) ... FAIL',
                    'test_simple_ok (test_scripts.simple.TestSimple) ... ok',
                    'test_simple_skip (test_scripts.simple.TestSimple) ... SKIP'])


class TestSimpleClass(NoseDepPluginTester):
    suitepath = "test_scripts/simple.py:TestSimple"

    def runTest(self):
        self.check(['test_simple_fail (test_scripts.simple.TestSimple) ... FAIL',
                    'test_simple_ok (test_scripts.simple.TestSimple) ... ok',
                    'test_simple_skip (test_scripts.simple.TestSimple) ... SKIP'])


class TestSimpleClassTestOK(NoseDepPluginTester):
    suitepath = "test_scripts/simple.py:TestSimple.test_simple_ok"

    def runTest(self):
        self.check(['test_simple_ok (test_scripts.simple.TestSimple) ... ok'])


class TestSimpleClassTestSKIP(NoseDepPluginTester):
    suitepath = "test_scripts/simple.py:TestSimple.test_simple_skip"

    def runTest(self):
        self.check(['test_simple_skip (test_scripts.simple.TestSimple) ... SKIP'])


class TestSimpleClassTestFAIL(NoseDepPluginTester):
    suitepath = "test_scripts/simple.py:TestSimple.test_simple_fail"

    def runTest(self):
        self.check(['test_simple_fail (test_scripts.simple.TestSimple) ... FAIL'])


class TestDecoratedFunctionalAll(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_tests.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_dft_f ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_b ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_e ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_a ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_c ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_d ... ok'])


class TestDecoratedFunctionalDepSkip(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_dep_skip.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_dep_skip.test_dfds_c ... ok',
                    'test_scripts.decorated_functional_dep_skip.test_dfds_b ... FAIL',
                    'test_scripts.decorated_functional_dep_skip.test_dfds_e ... SKIP: skippington',
                    'test_scripts.decorated_functional_dep_skip.test_dfds_a ... SKIP:'
                    ' Required test \'test_dfds_b\' FAILED',
                    'test_scripts.decorated_functional_dep_skip.test_dfds_d ... ERROR',
                    'test_scripts.decorated_functional_dep_skip.test_dfds_f ... SKIP:'
                    ' Required test \'test_dfds_e\' SKIPPED'])


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
    suitepath = "test_scripts/decorated_functional_tests.py:test_dft_d"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_dft_b ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_a ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_d ... ok'])


class TestDecoratedFunctionalSpecificNoDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_tests.py:test_dft_f"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_dft_f ... ok'])


class TestDecoratedFunctionalSpecificC(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_tests.py:test_dft_c"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_tests.test_dft_b ... ok',
                    'test_scripts.decorated_functional_tests.test_dft_c ... ok'])


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


class TestDecoratedSubclass(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_subclass.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_method_subclass.TestNoseDecoratedChild.test_cd_a ... ok',
                    'test_scripts.decorated_method_subclass.TestNoseDecoratedChild.test_cd_c ... ok',
                    'test_scripts.decorated_method_subclass.TestNoseDecoratedChild.test_cd_b ... ok'])


class TestDecoratedSubclassTestCase(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_subclass_testcase.py:"

    def runTest(self):
        self.check(
            ['test_cdt_a (test_scripts.decorated_method_subclass_testcase.TestNoseDecoratedTestCaseChild) ... ok',
             'test_cdt_c (test_scripts.decorated_method_subclass_testcase.TestNoseDecoratedTestCaseChild) ... ok',
             'test_cdt_b (test_scripts.decorated_method_subclass_testcase.TestNoseDecoratedTestCaseChild) ... ok'])


class TestDecoratedMethodSpecificNoDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_tests.py:TestNoseDecoratedMethod.test_cd_a"

    def runTest(self):
        self.check(['test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_a ... ok'])


class TestDecoratedMethodSpecificDep(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_tests.py:TestNoseDecoratedMethod.test_cd_b"

    def runTest(self):
        self.check(['test_scripts.decorated_method_tests.TestNoseDecoratedMethod.test_cd_b ... ok'])


class TestDecoratedFunctionalPriority(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_functional_priority.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_functional_priority.test_dfp_b ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_a ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_f ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_g ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_h ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_i ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_d ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_e ... ok',
                    'test_scripts.decorated_functional_priority.test_dfp_c ... ok'])


class TestDecoratedMethodPriority(NoseDepPluginTester):
    suitepath = "test_scripts/decorated_method_priority.py:"

    def runTest(self):
        self.check(['test_scripts.decorated_method_priority.TestMP.test_dmp_b ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_c ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_a ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_f ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_g ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_h ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_i ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_d ... ok',
                    'test_scripts.decorated_method_priority.TestMP.test_dmp_e ... ok'])


class TestDecoratedDirectory2Levels(NoseDepPluginTester):
    suitepath = "test_scripts/dir_test/dir_test_2:"

    def runTest(self):
        self.check(['test_04 (dir_test_2.dir_tests.display_node_list) ... ok',
                    'test_03 (dir_test_2.dir_tests.display_node_list) ... ok',
                    'test_02 (dir_test_2.dir_tests.display_node_list) ... ok',
                    'test_01 (dir_test_2.dir_tests.display_node_list) ... ok'])


class TestDecoratedDirectoryDirect(NoseDepPluginTester):
    suitepath = "test_scripts/dir_test/dir_test_2/dir_tests.py:"

    def runTest(self):
        self.check(['test_04 (dir_test_2.dir_tests.display_node_list) ... ok',
                    'test_03 (dir_test_2.dir_tests.display_node_list) ... ok',
                    'test_02 (dir_test_2.dir_tests.display_node_list) ... ok',
                    'test_01 (dir_test_2.dir_tests.display_node_list) ... ok'])


class TestDependsNoArgument(NoseDepPluginTester):
    def test_no_args(self):
        pass

    def makeSuite(self):
        with assert_raises_regex(ValueError, r'depends decorator needs at least one argument'):
            class TC(unittest.TestCase):
                @depends()
                def run_test_no_args(self):
                    pass

            return [TC('run_test_no_args')]


class TestDependsSelf(NoseDepPluginTester):
    def test_self_dep(self):
        pass

    def makeSuite(self):
        with assert_raises_regex(ValueError, r'Test \'run_test_self_dep\' cannot depend on itself'):
            class TC(unittest.TestCase):
                @depends(after='run_test_self_dep')
                def run_test_self_dep(self):
                    pass

            return [TC('run_test_self_dep')]


if __name__ == '__main__':
    unittest.main()


# To test:
# * Multiple specifiers
# * Test both with file and __main__ specifying prefix
#   In the tested application use of __main__. tests all tests while filename prefix works.

# FIXME: Dependencies are global and not qualified. Would probably be best if
#        it contained unique qualifiers. (now we can't use the same test name in different files)
