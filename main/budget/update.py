from typing import List

from terminology import in_red, in_green

from main.budget.constants import get_new_transactions, get_current_transactions
from main.budget.transactions import TransactionsIterator, transform_row
from main.util.file_io import to_tsv
from util.data import Sheet


def update_spreadsheet(output_file: str):
    new: Sheet = get_new_transactions()
    current: Sheet = get_current_transactions()

    next_rows = combine(new, current)
    to_tsv(output_file, next_rows, show_diff=False)

    print("Update complete. Results outputted to", output_file)


def combine(new: Sheet, current: Sheet) -> List[List[str]]:
    new_iter: TransactionsIterator = TransactionsIterator(new)
    current_iter: TransactionsIterator = TransactionsIterator(current)

    next_rows: List[List[str]] = []
    while True:
        if new_iter.finished() and current_iter.finished():
            break

        new_key = new_iter.key()
        current_key = current_iter.key()
        if new_key == current_key:
            # print("Same row:", current_key, current_iter.row())
            next_rows.append(current_iter.row())
            new_iter.next()
            current_iter.next()
        elif new_iter.date() < current_iter.date():
            if not new_iter.finished():
                print(in_red(f'Non-transaction row: {current_key}, {new_key}'))
                current_iter.add_label("MINTLESS")
            next_rows.append(current_iter.row())
            current_iter.next()
        else:
            transformed_row = transform_row(new, current, new_iter.row())
            print(in_green(f'New row: {new_key}, {transformed_row}'))
            next_rows.append(transformed_row)
            new_iter.next()

    return next_rows

