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

It do however support running the necessary dependencies for a single test,
thus if you specify to run only test B and test B depends on A; then A will
run before B to satisfy that dependency.
"""
from itertools import chain

import string
from collections import defaultdict
from functools import partial, wraps
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
    if func is None:
        return partial(depends, after=after, before=before)

    def self_check(a, b):
        if a == b:
            raise ValueError("Test '{}' cannot depend on itself".format(a))

    def handle_dep(cond, _before=True):
        if cond:
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

    def __init__(self):
        super(DepLoader, self).__init__()
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

    def options(self, parser, env):
        super(self.__class__, self).options(parser, env)

    def configure(self, options, conf):
        super(self.__class__, self).configure(options, conf)

    def prepareTestLoader(self, _):
        self.loader = DepLoader()
        return self.loader

    def orderTests(self, all_tests, test):
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
        all_tests = {}
        for s in suite:
            all_tests[string.split(str(s), '.')[-1]] = s

        return self.orderTests(all_tests, suite)

    def prepareTest(self, test):
        all_tests = {}
        for t in test:
            for tt in t:
                if isinstance(tt, ContextSuite):  # MethodTestCase
                    all_tests[tt.context.__name__] = self.prepareSuite(tt)
                    setattr(all_tests[tt.context.__name__], 'nosedep_run', True)
                else:  # FunctionTestCase
                    all_tests[tt.test.test.__name__] = tt

        return self.orderTests(all_tests, test)
