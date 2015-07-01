from unittest import SkipTest
from nosedep import depends


@depends(after='test_dfds_b')
def test_dfds_a():
    pass


def test_dfds_b():
    raise AssertionError("UNGA HAZA")


def test_dfds_c():
    pass


@depends(after='not_existing_test')
def test_dfds_d():
    pass


def test_dfds_e():
    raise SkipTest('skippington')


@depends(after=test_dfds_e)
def test_dfds_f():
    pass
