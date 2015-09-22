from nosedep import depends, default_priority


@depends(priority=2)
def test_dfp_a():
    pass


@depends(priority=1)
def test_dfp_b():
    pass


# Setting priority above the default to force this
# to be tested last.
@depends(priority=default_priority+1)
def test_dfp_c():
    pass


@depends(priority=5, after='test_dfp_f')
def test_dfp_d():
    pass


@depends(priority=5, after='test_dfp_d')
def test_dfp_e():
    pass


@depends(priority=5)
def test_dfp_f():
    pass


@depends(priority=1, after='test_dfp_a')
def test_dfp_g():
    pass


@depends(priority=2, after='test_dfp_a')
def test_dfp_h():
    pass


@depends(priority=3, after='test_dfp_a')
def test_dfp_i():
    pass
