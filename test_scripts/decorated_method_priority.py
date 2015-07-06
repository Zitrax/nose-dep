from nosedep import depends


class TestMP(object):
    @depends(priority=2)
    def test_dmp_a(self):
        pass

    @depends(priority=1)
    def test_dmp_b(self):
        pass

    @depends(priority=3)
    def test_dmp_c(self):
        pass

    @depends(priority=5, after='test_dmp_f')
    def test_dmp_d(self):
        pass

    @depends(priority=5, after='test_dmp_d')
    def test_dmp_e(self):
        pass

    @depends(priority=5)
    def test_dmp_f(self):
        pass

    @depends(priority=1, after='test_dmp_a')
    def test_dmp_g(self):
        pass

    @depends(priority=2, after='test_dmp_a')
    def test_dmp_h(self):
        pass

    @depends(priority=3, after='test_dmp_a')
    def test_dmp_i(self):
        pass


# Order should be
# NP: b1, c3
# PG1: f5, a2
# PG2: d5,g1,h2,i3
# PG3: e5
#
# => b, c, a, f, g, h, i, d, e
