import unittest

from main.budget.update import combine


class CombineTestCase(unittest.TestCase):
    mint_schema = [
        'Date',
        'Description',
        'Original Description',
        'Amount',
        'Transaction Type',
        'Category',
        'Account Name',
        'Labels',
        'Notes',
    ]
    sheets_schema = [
        'Date',
        'Description',
        'Original Description',
        'Amount',
        'Category',
        'Another Category',
        'Labels',
        'Notes',
    ]

    def test_equal_use_sheets(self):
        mint_rows = [
            self.mint_schema,
            [
                '2/21/2023', 'Desc', 'Original Desc', '3852.48', 'Ignored Transaction Type',
                'Wrong Category', 'Ignored Account Name', 'Wrong Label', 'Wrong Notes'
            ]
        ]
        sheets_rows = [
            self.sheets_schema,
            [
                '02/21/2023', 'Desc', 'Original Desc', '3852.48',
                'Correct Category', 'Correct Label', 'Correct Notes'
            ]
        ]
        new_rows = combine(mint_rows, sheets_rows)
        self.assertListEqual(
            sheets_rows,
            new_rows,
        )

    def test_transform(self):
        mint_rows = [
            self.mint_schema,
            [
                '2/21/2023', 'Desc', 'Original Desc', '3852.48', 'Ignored Transaction Type',
                'Category', 'Ignored Account Name', 'Label', 'Notes'
            ]
        ]
        sheets_rows = [self.sheets_schema]
        expected_rows = [
            self.sheets_schema,
            [
                '02/21/2023', 'February 2023', 'Desc', 'Original Desc', '3852.48',
                'Category', '', 'Label', 'Notes'
            ]
        ]

        new_rows = combine(mint_rows, sheets_rows)

        self.assertListEqual(
            expected_rows,
            new_rows,
        )


if __name__ == '__main__':
    unittest.main()
