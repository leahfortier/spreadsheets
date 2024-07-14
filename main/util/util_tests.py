import unittest

from general import all_unique


class GeneralUtilsTestCase(unittest.TestCase):
    def test_all_unique(self):
        self.assertTrue(all_unique(["A", "a", "b"]))
        self.assertTrue(all_unique(["A"]))
        self.assertTrue(all_unique([]))
        self.assertFalse(all_unique(["A", "A", "b"]))
        self.assertFalse(all_unique(["A", "--", "--"]))
        self.assertTrue(all_unique(["A", "--", "--"], ["--"]))


if __name__ == '__main__':
    unittest.main()
