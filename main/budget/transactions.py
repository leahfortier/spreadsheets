from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from main.budget.constants import DATE_FORMAT, START_DATE, TransactionFields
from util.data import Sheet


def transform_row(new: Sheet, current: Sheet, new_row: List[str]) -> List[str]:
    transformed_row = ['']*len(current.schema)

    for field in new.schema_row:
        if field in current.schema:
            value = new.get(new_row, field)
            current.set(transformed_row, field, value)

    return transformed_row


class TransactionsIterator:
    def __init__(self, transactions: Sheet):
        self.transactions = transactions
        self.index = 0

    def next(self) -> None:
        self.index += 1

    def finished(self) -> bool:
        return self.date() < START_DATE

    def row(self) -> List[str]:
        return self.transactions.rows[self.index]

    def date(self) -> datetime:
        if self.index >= len(self.transactions.rows):
            return START_DATE - timedelta(days=1)
        date_field = self.transactions.get(self.row(), TransactionFields.DATE)
        return datetime.strptime(date_field, DATE_FORMAT)

    def key(self) -> Optional[Tuple[str, ...]]:
        if self.finished():
            return None
        return self.transactions.get_id(self.row())

    def add_label(self, label: str) -> None:
        current_label = self.transactions.get(self.row(), TransactionFields.LABELS)
        new_label = (current_label + "\n" + label).strip()
        self.transactions.set(self.row(), TransactionFields.LABELS, new_label)
