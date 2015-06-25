from nosedep import depends


@depends(after=['test_dfm_b', 'test_dfm_c'])
def test_dfm_a():
    pass


def test_dfm_b():
    pass


def test_dfm_c():
    pass
