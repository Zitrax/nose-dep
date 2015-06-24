from nosedep import depends
from nose.tools import assert_true, assert_false


class TestNoseDecoratedMethod(object):
    did_setup_class = False
    did_teardown_class = False

    @classmethod
    def reset(cls):
        print "RESET"
        cls.did_setup_class = False
        cls.did_teardown_class = False

    def __init__(self):
        self.did_setup = False
        self.did_teardown = False

    @classmethod
    def setup_class(cls):
        cls.did_setup_class = True
        # Would be better to reset this externally
        cls.did_teardown_class = False

    @classmethod
    def teardown_class(cls):
        cls.did_teardown_class = True

    def setup(self):
        self.did_setup = True

    def teardown(self):
        self.did_teardown = True

    def test_cd_a(self):
        assert_true(self.did_setup)
        assert_true(self.did_setup_class)
        assert_false(self.did_teardown)
        assert_false(self.did_teardown_class)

    def test_cd_b(self):
        pass

    @depends(before='test_cd_b')
    def test_cd_c(self):
        pass
