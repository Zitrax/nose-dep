import unittest
from nosedep import depends

class display_node_list(unittest.TestCase):
    @depends(after='test_02')
    def test_01(self):
        pass

    @depends(after='test_03')
    def test_02(self):
        pass

    @depends(after='test_04')
    def test_03(self):
        pass

    def test_04(self):
        pass
