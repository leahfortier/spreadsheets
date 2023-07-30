from typing import List
import csv


path = '../'


def with_path(filename: str) -> str:
    return path + filename


def from_file(filename: str) -> List[str]:
    with open(filename, 'r') as file:
        return file.read().splitlines()


def to_file(filename: str, rows: List[str]) -> None:
    with open(filename, 'w') as file:
        file.writelines(row + '\n' for row in rows)


def to_csv(filename: str, rows: List[List[str]], delimiter: str = ',') -> None:
    with open(filename, 'w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=delimiter)
        csv_writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {filename}")


def from_csv(filename: str, delimiter: str = ',') -> List[List[str]]:
    rows: List[List[str]] = []
    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_reader:
            rows.append(row)
    return rows


def to_tsv(filename: str, rows: List[List[str]]) -> None:
    to_csv(filename, rows, delimiter='\t')


def from_tsv(filename: str) -> List[List[str]]:
    return from_csv(filename, delimiter='\t')