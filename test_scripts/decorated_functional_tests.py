from nosedep import depends


@depends(after='test_dft_b')
def test_dft_a():
    pass


def test_dft_b():
    pass


@depends(after='test_dft_b')
def test_dft_c():
    pass


@depends(after='test_dft_a')
def test_dft_d():
    pass


@depends(before='test_dft_c')
def test_dft_e():
    pass


def test_dft_f():
    pass
