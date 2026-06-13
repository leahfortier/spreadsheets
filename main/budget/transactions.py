from typing import List

from main.budget.constants import TransactionFields
from util.data import Sheet


def transform_row(new: Sheet, current: Sheet, new_row: List[str]) -> List[str]:
    transformed_row = ['']*len(current.schema)

    for field in new.schema_row:
        if field in current.schema:
            value = new.get(new_row, field)
            current.set(transformed_row, field, value)

    return transformed_row


def add_label(transactions: Sheet, row: List[str], label: str) -> None:
    current_label = transactions.get(row, TransactionFields.LABELS)
    new_label = (current_label + "\n" + label).strip()
    transactions.set(row, TransactionFields.LABELS, new_label)
