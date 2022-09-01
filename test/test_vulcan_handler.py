import unittest
from handlers.vulcan_handler import VulcanHandler
import numpy as np

class TestVulcanCase(unittest.TestCase):
    def test_onlyrun(self):
        case = VulcanHandler(['./data/3D-Base.dat'], 'newcase', folderTemp="./data/temp/")
        res = case.run({})
        allRes = res.getAllResults()
        step = 210.0
        toCheck = np.arange(0, step*1001, step)
        np.testing.assert_allclose(allRes['stress'][:,1,0], toCheck)

    def test_oneparameterrun(self):
        case = VulcanHandler(['./data/3D-Base-EPARAM.dat'], 'newcase', folderTemp="./data/temp/")
        res = case.run({'E': 100.0E3})
        allRes = res.getAllResults()
        step = 100.0
        toCheck = np.arange(0, step*1001, step)
        np.testing.assert_allclose(allRes['stress'][:,1,0], toCheck)


if __name__ == '__main__':
    unittest.main()