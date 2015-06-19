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

from collections import defaultdict
from functools import partial, wraps
from nose.plugins import Plugin
from toposort import toposort_flatten

dependencies = defaultdict(set)
order = None


def depends(func=None, after=None, before=None):
    """
    Decorator to specify test dependencies.

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


class NoseDep(Plugin):
    name = "nosedep"
    score = 100

    def __init__(self):
        super(NoseDep, self).__init__()

    def options(self, parser, env):
        super(self.__class__, self).options(parser, env)

    def configure(self, options, conf):
        global order
        super(self.__class__, self).configure(options, conf)
        if self.enabled:
            # Calculate dependencies
            order = toposort_flatten(dependencies)

    # noinspection PyMethodMayBeStatic
    def prepareTest(self, test):
        global order
        all_tests = {}
        for t in test._tests:
            for tt in t:
                all_tests[tt.test.test.__name__] = tt
        test._tests = (all_tests[t] for t in order)
        return test
