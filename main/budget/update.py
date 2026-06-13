from typing import List, Set, Tuple

from terminology import in_red

from main.budget.constants import get_new_transactions, get_current_transactions
from main.budget.transactions import transform_row, add_label
from main.util.file_io import to_tsv
from util.data import Sheet


def update_spreadsheet(output_file: str):
    new: Sheet = get_new_transactions()
    current: Sheet = get_current_transactions()

    next_rows = combine(new, current)
    to_tsv(output_file, next_rows, show_diff=False)

    print("Update complete. Results outputted to", output_file)


def combine(new: Sheet, current: Sheet) -> List[List[str]]:
    current_seen: Set[Tuple[str, ...]] = set()

    next_rows: List[List[str]] = []
    for row_index, row in enumerate(new.rows):
        key = new.row_ids[row_index]
        assert key not in current_seen
        if key in current.id_map:
            # print("Same row:", key)
            next_rows.append(current.get_row(*key))
            current_seen.add(key)
        else:
            transformed_row = transform_row(new, current, row)
            # print(in_green(f'New row: {key}, {transformed_row}'))
            next_rows.append(transformed_row)

    for row_index, row_id in enumerate(current.row_ids):
        if row_id not in current_seen:
            print(in_red(f'Non-transaction row: {row_id}'))
            row = current.rows[row_index]
            add_label(current, row, "MINTLESS")
            next_rows.append(row)

    return next_rows

