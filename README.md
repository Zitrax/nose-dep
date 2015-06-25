Nosetest plugin for test dependencies.

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
