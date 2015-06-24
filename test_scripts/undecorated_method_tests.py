from nose.tools import assert_true, assert_false


class TestNoseUndecoratedMethod(object):
    did_setup_class = False
    did_teardown_class = False

    def __init__(self):
        self.did_setup = False
        self.did_teardown = False

    @classmethod
    def setup_class(cls):
        cls.did_setup_class = True

    @classmethod
    def teardown_class(cls):
        cls.did_teardown_class = True

    def setup(self):
        self.did_setup = True

    def teardown(self):
        self.did_teardown = True

    def test_c_a(self):
        assert_true(self.did_setup)
        assert_true(self.did_setup_class)
        assert_false(self.did_teardown)
        assert_false(self.did_teardown_class)

    def test_c_b(self):
        pass
