from typing import List

from main.budget.constants import SPREADSHEET_ID
from main.budget.constants import TRANSACTIONS_FILE
from main.budget.constants import TRANSACTIONS_TAB
from main.budget.transactions import Transactions, TransactionsIterator
from main.util.file_io import from_csv, to_csv, to_tsv
from main.util.sheets import get_sheet_data


def update_spreadsheet(output_file: str, backup_file: str):
    new_rows: List[List[str]] = from_csv(TRANSACTIONS_FILE)
    current_rows: List[List[str]] = get_sheet_data(SPREADSHEET_ID, TRANSACTIONS_TAB)

    next_rows = combine(new_rows, current_rows)
    to_tsv(output_file, next_rows, show_diff=False)
    to_tsv(backup_file, current_rows, show_diff=False)


def combine(new_rows: List[List[str]], current_rows: List[List[str]]) -> List[List[str]]:
    new: Transactions = Transactions(new_rows)
    current: Transactions = Transactions(current_rows)

    new_iter: TransactionsIterator = TransactionsIterator(new)
    current_iter: TransactionsIterator = TransactionsIterator(current)

    next_rows: List[List[str]] = [current.schema_row]
    while True:
        if new_iter.finished() and current_iter.finished():
            break

        new_key = new_iter.key()
        current_key = current_iter.key()
        if new_key == current_key:
            # print("Same row:", current_key, current_iter.get())
            next_rows.append(current_iter.get())
            new_iter.next()
            current_iter.next()
        elif new_iter.date() < current_iter.date():
            print("Non-transaction row:", current_key, current_iter.get())
            next_rows.append(current_iter.with_label("MINTLESS"))
            current_iter.next()
        else:
            transformed_row = new_iter.transform(current.schema)
            # print("New row:", new_key, transformed_row)
            next_rows.append(transformed_row)
            new_iter.next()

    return next_rows
