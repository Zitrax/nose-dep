from collections import defaultdict
from functools import partial, wraps
from nose.plugins import Plugin
from toposort import toposort_flatten

dependencies = defaultdict(set)
order = None


def depends(func=None, after=None, before=None):
    if not after and not before:
        raise ValueError("depends decorator needs at least one argument")
    if func is None:
        return partial(depends, after=after, before=before)

    if after:
        dependencies[func.__name__].add(after)
    if before:
        dependencies[after].add(func.__name__)

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
