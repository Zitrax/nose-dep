from unittest import SkipTest, TestCase

class undecorated_method_classes(TestCase):
    def test_umc_a(self):
        pass

    def test_umc_b(self):
        pass

class descendent1(undecorated_method_classes):
    pass

class descendent2(descendent1):
    pass
