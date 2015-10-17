## Nosetest plugin for test dependencies.

Normally tests should not depend on each other - and it should be avoided
as long as possible. Optimally each test should be able to run in isolation.

However there might be rare cases or special circumstances where one would
want this. For example very slow integration tests where redoing what test
A did just to run test B would simply be too costly. Or temporarily while
testing or debugging. It's also possible that one wants some test to run first
as 'smoke tests' such that the rest can be skipped if those tests fail.

The current implementation allows marking tests with the `@depends` decorator
where it can be declared if the test needs to run before or after some
other specific test(s).

There is also support for skipping tests based on the dependency results,
thus if test B depends on test A and test A fails then B will be skipped
with the reason that A failed.

Nosedep also supports running the necessary dependencies for a single test,
thus if you specify to run only test B and test B depends on A; then A will
run before B to satisfy that dependency.

Note that 'before' dependencies are treated as soft. A soft dependency will only
affect the test ordering, not force inclusion. For example if we have::

    def test_a:
      pass

    @depends(before=test_a)
    def test_b:
      pass

and run all tests they would run in the order b,a. If you specify to run only
either one of them only that test would run. However changing it to::

    @depends(after=test_b)
    def test_a:
      pass

    def test_b:
      pass

would affect the case when you specify to run only test a, since it would have
to run test b first to specify the 'after' dependency since it's a 'hard' dependency.

Finally there is prioritization support. Each test can be given an integer priority
and the tests will run in order from lowest to highest. Dependencies take
precedence so in total the ordering will be:

1. All tests with a priority lower or equal to the default that are not part of any
   dependency chain ordered first by priority then by name.
2. Priority groups in order, while each priority group is internally ordered
   the same as point 1.
3. All tests with priority higher than the default that are not part of any
   dependency chain ordered first by priority then by name.

Default priority if not specified is 50.

*Note: Currently no support for Python 2.6 and 3.2. Should work for 2.7 and 3.3+.*

## Info

* [![Code Quality](https://landscape.io/github/Zitrax/node-dep/master/landscape.png)](https://landscape.io/github/Zitrax/node-dep/master)
* [![Build Status](https://travis-ci.org/Zitrax/nose-dep.svg?branch=master)](https://travis-ci.org/Zitrax/nose-dep)
* [![Coverage Status](https://coveralls.io/repos/Zitrax/nose-dep/badge.svg?branch=master&service=github)](https://coveralls.io/github/Zitrax/nose-dep?branch=master)

## TODO

* Strict roles such as "smoke" that cause everything to be skipped if it's not ok