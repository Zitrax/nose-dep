"""Nosetest plugin for test dependencies.

Normally tests should not depend on each other - and it should be avoided
as long as possible. Optimally each test should be able to run in isolation.

However there might be rare cases or special circumstances where one would
want this. For example very slow integration tests where redoing what test
A did just to run test B would simply be too costly. Or temporarily while
testing or debugging.

The current implementation allows marking tests with the @depends decorator
where it can be declared if the test needs to run before or after some
other specific test(s).

There is also support for skipping tests based on the dependency results,
thus if test B depends on test A and test A fails then B will be skipped
with the reason that A failed.

Nosedep also supports running the necessary dependencies for a single test,
thus if you specify to run only test B and test B depends on A; then A will
run before B to satisfy that dependency.
"""
from itertools import chain
import string
from collections import defaultdict
from functools import partial, wraps
import sys

from nose.loader import TestLoader
from nose.plugins import Plugin
from nose.suite import ContextSuite
from toposort import toposort_flatten

dependencies = defaultdict(set)


def depends(func=None, after=None, before=None):
    """Decorator to specify test dependencies

    :param after: The test needs to run after this/these tests. String or list of strings.
    :param before: The test needs to run before this/these tests. String or list of strings.
    """
    if not after and not before:
        raise ValueError("depends decorator needs at least one argument")

    # This avoids some nesting in the decorator
    # If called without func the decorator was called with optional args
    # so we'll return a function with those args filled in.
    if func is None:
        return partial(depends, after=after, before=before)

    def self_check(a, b):
        if a == b:
            raise ValueError("Test '{}' cannot depend on itself".format(a))

    def handle_dep(conditions, _before=True):
        if conditions:
            if not hasattr(conditions, '__iter__'):
                conditions = [conditions]
            for cond in conditions:
                if hasattr(cond, '__call__'):
                    cond = cond.__name__
                self_check(func.__name__, cond)
                if _before:
                    dependencies[cond].add(func.__name__)
                else:
                    dependencies[func.__name__].add(cond)

    handle_dep(before)
    handle_dep(after, False)

    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner


class DepLoader(TestLoader):
    """Loader that stores what was specified but still loads all tests"""

    # noinspection PyPep8Naming
    def __init__(self, config=None, importer=None, workingDir=None, selector=None):
        super(DepLoader, self).__init__(config, importer, workingDir, selector)
        self.tests = []

    def loadTestsFromName(self, name, module=None, discovered=False):
        """Need to load all tests since we might have dependencies"""
        parts = string.split(name, ':' if ':' in name else '.')
        if len(parts) == 2 and parts[1]:
            self.tests.append(parts[-1].split('.')[-1])
        return super(DepLoader, self).loadTestsFromName(parts[0], module, discovered)


class NoseDep(Plugin):
    """Allow specifying test dependencies with the depends decorator."""
    name = "nosedep"
    score = 100

    def __init__(self):
        super(NoseDep, self).__init__()
        self.loader = None
        self.ok_results = set()
        self.results = None

    def options(self, parser, env):
        super(self.__class__, self).options(parser, env)

    def configure(self, options, conf):
        super(self.__class__, self).configure(options, conf)

    def prepareTestLoader(self, loader):
        self.loader = DepLoader(loader.config, loader.importer, loader.workingDir, loader.selector)
        return self.loader

    def orderTests(self, all_tests, test):
        """Determine test ordering based on the dependency graph"""
        order = toposort_flatten(dependencies)
        if self.loader.tests:  # If specific tests were mentioned on the command line
            def mark_deps(t):
                if t in dependencies:
                    for dep in dependencies[t]:
                        setattr(all_tests[dep], 'nosedep_run', True)
                        mark_deps(dep)

            for t in self.loader.tests:
                if t in all_tests:
                    setattr(all_tests[t], 'nosedep_run', True)
                    mark_deps(t)

            def should_test(t):
                return t in all_tests and getattr(all_tests[t], 'nosedep_run', False)

            no_deps = (all_tests[t] for t in all_tests.keys() if t not in order and should_test(t))
            deps = (all_tests[t] for t in order if should_test(t))

            test._tests = chain(no_deps, deps)
        else:  # If we should run all tests
            no_deps = (all_tests[t] for t in sorted(all_tests.keys()) if t not in order)
            deps = (all_tests[t] for t in order if t in all_tests)
            test._tests = chain(no_deps, deps)
        return test

    def prepareSuite(self, suite):
        """Prepare suite and determine test ordering"""
        all_tests = {}
        for s in suite:
            all_tests[string.split(str(s), '.')[-1]] = s

        return self.orderTests(all_tests, suite)

    def prepareTest(self, test):
        """Prepare and determine test ordering"""
        all_tests = {}
        try:
            for t in test:
                for tt in t:
                    if isinstance(tt, ContextSuite):  # MethodTestCase
                        all_tests[tt.context.__name__] = self.prepareSuite(tt)
                        setattr(all_tests[tt.context.__name__], 'nosedep_run', True)
                    else:  # FunctionTestCase
                        all_tests[tt.test.test.__name__] = tt
        except AttributeError as e:
            # This exception is confusing by default - add some further info
            t, v, tb = sys.exc_info()
            v = AttributeError(e.message + " - Due to: " + str(tt))
            raise t, v, tb

        return self.orderTests(all_tests, test)

    def dependency_failed(self, test):
        """Returns an error string if any of the dependencies failed"""
        for d in (self.test_name(i) for i in dependencies[test]):
            if d in (self.test_name(str(t[0])) for t in self.results.failures):
                return "Required test '{}' FAILED".format(d)
            if d in (self.test_name(str(t[0])) for t in self.results.errors):
                return "Required test '{}' ERRORED".format(d)
            if d in (self.test_name(str(t[0])) for t in self.results.skipped):
                return "Required test '{}' SKIPPED".format(d)
        return None

    def dependency_ran(self, test):
        """Returns an error string if any of the dependencies did not run"""
        for d in (self.test_name(i) for i in dependencies[test]):
            if d not in self.ok_results:
                return "Required test '{}' did not run (does it exist?)".format(d)
        return None

    def beforeTest(self, test):
        """Skip or Error the test if the dependencies are not fulfilled"""
        tn = self.test_name(test)
        res = self.dependency_failed(tn)
        if res:
            test.test.skipTestNoseDep = partial(test.test.skipTest, res)
            test.test._testMethodName = 'skipTestNoseDep'
            return
        res = self.dependency_ran(tn)
        if res:
            def error_test():
                raise Exception(res)
            test.test.errTestNoseDep = error_test
            test.test._testMethodName = 'errTestNoseDep'

    @staticmethod
    def test_name(test):
        # Internally we are currently only using the method/function names
        # could be that we might want to use the full qualified name in the future
        return str(test).split('.')[-1]

    def addSuccess(self, test):
        """The result object does not store successful results, so we have to do it"""
        self.ok_results.add(self.test_name(test))

    def prepareTestResult(self, result):
        """Store the result object so we can inspect it in beforeTest"""
        self.results = result
