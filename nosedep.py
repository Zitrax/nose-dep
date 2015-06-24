"""Nosetest plugin for test dependencies.

Normally tests should not depend on each other - and it should be avoided
as long as possible. Optimally each test should be able to run in isolation.

However there might be rare cases where one would want this. For example
very slow integration tests where redoing what test A did just to run
test B would simply be too costly. Or temporarily while testing or debugging.

The current implementation allows marking tests with the @depends decorator
where it can be declared if the test needs to run before or after some
specific test(s).

Currently this just determines the test order, thus even if test B depends
on test A and A failed B will still run. In the future we might want to
skip test B and all other remaining tests in the affected dependency chain.
"""
from itertools import chain

import string
from collections import defaultdict
from functools import partial, wraps
from nose.loader import TestLoader
from nose.plugins import Plugin
from toposort import toposort_flatten

dependencies = defaultdict(set)
order = None


def depends(func=None, after=None, before=None):
    """Decorator to specify test dependencies

    :param after: The test needs to run after this/these tests. String or list of strings.
    :param before: The test needs to run before this/these tests. String or list of strings.
    """
    if not after and not before:
        raise ValueError("depends decorator needs at least one argument")
    if func is None:
        return partial(depends, after=after, before=before)

    def self_check(a, b):
        if a == b:
            raise ValueError("Test '{}' cannot depend on itself".format(a))

    if after:
        self_check(func.__name__, after)
        dependencies[func.__name__].add(after)
    if before:
        self_check(func.__name__, before)
        dependencies[before].add(func.__name__)

    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)
    return inner


class DepLoader(TestLoader):
    """Loader that stores what was specified but still loads all tests"""

    def __init__(self):
        super(DepLoader, self).__init__()
        self.tests = []

    def loadTestsFromName(self, name, module=None, discovered=False):
        """Need to load all tests since we might have dependencies"""
        parts = string.split(name, ':' if ':' in name else '.', maxsplit=1)
        if len(parts) == 2:
            self.tests.append(parts[1])
        #print parts
        return super(DepLoader, self).loadTestsFromName(parts[0], module, discovered)


class NoseDep(Plugin):
    name = "nosedep"
    score = 100

    def __init__(self):
        super(NoseDep, self).__init__()
        self.loader = None

    def options(self, parser, env):
        super(self.__class__, self).options(parser, env)

    def configure(self, options, conf):
        global order
        super(self.__class__, self).configure(options, conf)
        if self.enabled:
            # Calculate dependencies
            order = toposort_flatten(dependencies)

    def prepareTestLoader(self, _):
        self.loader = DepLoader()
        return self.loader

    def prepareSuite(self, suite):
        # FIXME: This is horribly similar to prepareTest
        #        should share code
        # ----------------------------------------------
        # Diff is the all_tests collection and the check "t in all_tests"

        all_tests = {}
        for s in suite:
            print s.address()[-1]
            all_tests[s.address()[-1]] = s

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

            suite._tests = chain(no_deps, deps)
        else:  # If we should run all tests
            no_deps = (all_tests[t] for t in all_tests.keys() if t not in order)
            deps = (all_tests[t] for t in order if t in all_tests)
            suite._tests = chain(no_deps, deps)
        return suite

    # noinspection PyMethodMayBeStatic
    def prepareTest(self, test):
        global order
        all_tests = {}
        for t in test._tests:
            print "T:", type(t)
            for tt in t:
                # FIXME: Change check to not use protected member
                if hasattr(tt, '_tests'):  # MethodTestCase
                    all_tests[tt.context.__name__] = self.prepareSuite(tt)
                    setattr(all_tests[tt.context.__name__], 'nosedep_run', True)
                else:  # FunctionTestCase
                    all_tests[tt.test.test.__name__] = tt

        print all_tests
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
                return getattr(all_tests[t], 'nosedep_run', False)

            no_deps = (all_tests[t] for t in all_tests.keys() if t not in order and should_test(t))
            deps = (all_tests[t] for t in order if should_test(t))

            test._tests = chain(no_deps, deps)
        else:  # If we should run all tests
            no_deps = (all_tests[t] for t in all_tests.keys() if t not in order)
            deps = (all_tests[t] for t in order)
            test._tests = chain(no_deps, deps)
        return test
