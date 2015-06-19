from nose.tools import assert_true
from nosedep import depends


@depends(after='test_b')
def test_a():
    assert_true(True)


def test_b():
    assert_true(True)


if __name__ == '__main__':
    # Temporary for force testing using the plugin
    import nose
    from nosedep import NoseDep

    nose.main(defaultTest=__name__, addplugins=[NoseDep()])
