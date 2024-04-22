from typing import List

from main.budget.constants import SPREADSHEET_ID, TRANSACTIONS_TAB
from main.budget.doggy_bank import check_doggy_bank
from main.budget.transactions import Transactions
from main.budget.update import update_spreadsheet
from main.util.sheets import get_sheet_data


def main():
    update_spreadsheet("out/out_transactions.tsv", "out/backup_transactions.tsv")
    # check_duplicates()

    check_doggy_bank()


def check_duplicates():
    rows: List[List[str]] = get_sheet_data(SPREADSHEET_ID, TRANSACTIONS_TAB)
    transactions: Transactions = Transactions(rows)
    for index, row in enumerate(rows):
        if transactions.key_index[index] != 0:
            print(index, "Duplicate:", transactions.key(index))


main()
