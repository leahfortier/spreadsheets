from datetime import datetime, timedelta
from typing import List, Dict

from main.budget.constants import KEY_FIELDS, DATE, MONTH, CATEGORY, AMOUNT, TRANSACTION_TYPE, POSITIVE_TRANSACTION, \
    NEGATIVE_TRANSACTION, MONTH_FORMAT, DATE_FORMAT, START_DATE, ORIGINAL_DESCRIPTION, DESCRIPTION, LABELS


class Transactions:
    def __init__(self, rows: List[List[str]]):
        self.schema_row = rows[0]
        self.schema: Dict[str, int] = {}

        for i, val in enumerate(self.schema_row):
            self.schema[val] = i

        for field in KEY_FIELDS:
            assert field in self.schema

        self.rows: List[List[str]] = rows[1:]
        self.keys: Dict[str, int] = {}
        self.key_index: List[int] = [0]*len(rows)

        for row_index in range(0, len(self.rows)):
            while len(self.rows[row_index]) < len(self.schema_row):
                self.rows[row_index].append("")

            # Positive amount for refunds, negative for charges
            modifier = self.get_amount_modifier(row_index)
            amount = abs(float(self.get_value(row_index, AMOUNT)))
            self.set(row_index, AMOUNT, str(modifier*amount))

            # Trim all whitespace
            self._trim_value(row_index, ORIGINAL_DESCRIPTION)
            self._trim_value(row_index, DESCRIPTION)

            # Uniform date format (zero-indexed month/day)
            date = self.get_date_field(row_index)
            self.set(row_index, DATE, date.strftime(DATE_FORMAT))

            # Manually added column -- requires updates here and transform
            if MONTH in self.schema:
                self.set(row_index, MONTH, date.strftime(MONTH_FORMAT))

            # Key index for handling duplicates
            key_index = 0
            key = self._create_key(row_index, key_index)
            while key in self.keys:
                key_index += 1
                key = self._create_key(row_index, key_index)
            self.key_index[row_index] = key_index
            self.keys[key] = row_index

    def set(self, row_index: int, field: str, value: str):
        self.rows[row_index][self.schema[field]] = value

    def get_date_field(self, row_index: int) -> datetime:
        date_field = self.get_value(row_index, DATE)
        return datetime.strptime(date_field, "%m/%d/%Y")

    def get_amount_modifier(self, index: int) -> int:
        transaction_type = self.get_value(index, TRANSACTION_TYPE)
        if transaction_type == POSITIVE_TRANSACTION:
            return 1
        elif transaction_type == NEGATIVE_TRANSACTION:
            return -1
        print("Unknown transaction type:", transaction_type)
        return -1

    def get_value(self, row_index: int, field: str) -> str:
        return self.rows[row_index][self.schema[field]]

    def get_row(self, key: str) -> List[str]:
        return self.rows[self.keys[key]]

    def _trim_value(self, row_index: int, field: str):
        value = self.get_value(row_index, field)
        self.set(row_index, field, " ".join(value.split()))

    def _create_key(self, row_index: int, key_index: int) -> str:
        keys = [self.get_value(row_index, field) for field in KEY_FIELDS]
        keys.append(str(key_index))
        return "~~~".join(keys)

    def key(self, row_index: int) -> str:
        key_index = self.key_index[row_index]
        return self._create_key(row_index, key_index)

    def add_label(self, row_index: int, label: str):
        self.rows[row_index][self.schema[LABELS]] += "\n" + label
        self._trim_value(row_index, LABELS)

    def transform(self, row_index: int, schema: Dict[str, int]) -> List[str]:
        transformed_row = ['']*len(schema)

        for field, schema_index in schema.items():
            if field in self.schema:
                value = self.get_value(row_index, field)
                transformed_row[schema_index] = value

        date = self.get_date_field(row_index)
        transformed_row[schema[MONTH]] = date.strftime(MONTH_FORMAT)
        transformed_row[schema[CATEGORY]] = ''
        return transformed_row


class TransactionsIterator:
    def __init__(self, transactions: Transactions):
        self.transactions = transactions
        self.index = 0

    def next(self) -> None:
        self.index += 1

    def finished(self) -> bool:
        return self.date() < START_DATE

    def get(self) -> List[str]:
        return self.transactions.get_row(self.key())

    def date(self) -> datetime:
        if self.index >= len(self.transactions.rows):
            return START_DATE - timedelta(days=1)
        return self.transactions.get_date_field(self.index)

    def key(self) -> str:
        if self.finished():
            return ''
        return self.transactions.key(self.index)

    def with_label(self, label: str) -> List[str]:
        self.transactions.add_label(self.index, label)
        return self.get()

    def transform(self, schema: Dict[str, int]) -> List[str]:
        return self.transactions.transform(self.index, schema)
