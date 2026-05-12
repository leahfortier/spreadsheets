import unittest
from enum import Enum

from general import all_unique
from util.data import Sheet


class GeneralUtilsTestCase(unittest.TestCase):
    def test_all_unique(self):
        self.assertTrue(all_unique(["A", "a", "b"]))
        self.assertTrue(all_unique(["A"]))
        self.assertTrue(all_unique([]))
        self.assertFalse(all_unique(["A", "A", "b"]))
        self.assertFalse(all_unique(["A", "--", "--"]))
        self.assertTrue(all_unique(["A", "--", "--"], ["--"]))

class TestFields(str, Enum):
    DATE = "Date"
    DESCRIPTION = "Description"

class SheetDataTestCase(unittest.TestCase):
    def test_ids(self):
        rows = [
            [TestFields.DATE, TestFields.DESCRIPTION],
            ["01/01/2026", "test"],
            ["01/01/2026", "test 2"]
        ]
        sheet = Sheet(rows, id_fields=[TestFields.DATE], allow_duplicate_keys=True)
        print(sheet.id_map)


if __name__ == '__main__':
    unittest.main()
