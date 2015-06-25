from nosedep import depends


def test_dff_a():
    pass


@depends(before=test_dff_a)
def test_dff_b():
    pass


@depends(after=test_dff_b)
def test_dff_c():
    pass
