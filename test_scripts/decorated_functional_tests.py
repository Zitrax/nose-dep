from nosedep import depends


@depends(after='test_b')
def test_a():
    pass


def test_b():
    pass


@depends(after='test_b')
def test_c():
    pass


@depends(after='test_a')
def test_d():
    pass


@depends(before='test_c')
def test_e():
    pass


def test_f():
    pass
