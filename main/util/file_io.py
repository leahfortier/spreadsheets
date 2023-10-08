import os.path
from typing import List
import csv


path = '../'


def with_path(filename: str) -> str:
    return path + filename


def from_file(filename: str) -> List[str]:
    if not os.path.isfile(filename):
        return []

    with open(filename, 'r') as file:
        return file.read().splitlines()


def to_file(filename: str, rows: List[str], show_diff=True) -> None:
    if show_diff:
        compare_diff(filename, from_file(filename), rows)

    with open(filename, 'w') as file:
        file.writelines(row + '\n' for row in rows)


def compare_diff(filename: str, current_rows: List, new_rows: List):
    if not current_rows:
        return

    diff = len(new_rows) - len(current_rows)
    if diff > 0:
        print(f"Adding {diff} rows to {filename}")
    elif diff > 0:
        print(f"Removing {diff} rows to {filename}")
    else:
        for new_row, current_row in zip(new_rows, current_rows):
            if new_row != current_row:
                print(f"Updating {filename} row from {current_row} to {new_row}")
                if len(new_row) == len(current_row):
                    for index, (new_val, current_val) in enumerate(zip(new_row, current_row)):
                        if current_val != new_val:
                            print(f"\t{index} {current_val} -> {new_val}")


def to_csv(filename: str, rows: List[List[str]], delimiter: str = ',', show_diff=True) -> None:
    if show_diff:
        compare_diff(filename, from_csv(filename, delimiter), rows)

    with open(filename, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=delimiter)
        csv_writer.writerows(rows)


def from_csv(filename: str, delimiter: str = ',') -> List[List[str]]:
    rows: List[List[str]] = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_reader:
            rows.append(row)
    return rows


def to_tsv(filename: str, rows: List[List[str]], show_diff=True) -> None:
    to_csv(filename, rows, delimiter='\t', show_diff=show_diff)


def from_tsv(filename: str) -> List[List[str]]:
    return from_csv(filename, delimiter='\t')