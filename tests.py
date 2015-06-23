from nose.tools import assert_true
from nosedep import depends


@depends(after='test_b')
def test_a():
    assert_true(True)


def test_b():
    assert_true(True)


@depends(after='test_b')
def test_c():
    assert_true(True)


@depends(after='test_a')
def test_d():
    assert_true(True)


@depends(before='test_c')
def test_e():
    assert_true(True)


def test_f():
    pass


class TestNoseDep(object):
    def test_c_a(self):
        pass


if __name__ == '__main__':
    # Temporary for force testing using the plugin
    import nose
    from nosedep import NoseDep

    nose.main(defaultTest=__name__, addplugins=[NoseDep()])


# To test:
# * No specifier
# * Specifier for each functional test
# * Specifier for method tests
# * Multiple specifiers
# * Make sure a test that is not part of any dependency chain is tested
