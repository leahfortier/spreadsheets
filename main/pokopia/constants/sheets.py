from enum import Enum
from typing import List

from constants.sheet_id import POKOPIA_ID
from util.data import Sheet
from util.sheets_parse import get_sheet_data
from util.warn import GuardDog, message_guardian, WarnLevel


class RefFields(str, Enum):
    FAVORITES = "Favorites"


class DbFields(str, Enum):
    NAME = "Name"
    FAVORITES = "Favorites"


class ItemFields(str, Enum):
    NAME = "game name"
    ID = "serebii name / id"
    IMAGE_ID = "image id"
    SORT_ID = "sort"
    PAINT = "paint"
    PAINT_AMOUNT = "amount"
    BUY = "buy"
    SELL = "sell"
    STORAGE = "storage"


class TraderFields(str, Enum):
    ID = "id"
    BUY = "add buy"
    SELL = "add sell"
    PAINT = "add paint"
    PAINT_AMOUNT = "add amt"
    SORT = "sort"
    RAW_SORT = "raw sort"


TRADE_START = "trade start"
TRADE_END = "trade end"
TRADER_PREFIX = "Trader: "

YES_FAVE = "Y"
NO_FAVE = "N"


guard = GuardDog(level=WarnLevel.ASSERT)


@message_guardian(guard)
def _update_trader_schema(rows: List[List[str]]):
    schema = rows[0]
    helper = rows[1]
    trade_start = schema.index(TRADE_START)
    trade_end = schema.index(TRADE_END)
    for index in range(trade_start + 1, trade_end):
        trader_name = helper[index]
        guard.empty(schema[index], trader_name)
        schema[index] = TRADER_PREFIX + trader_name


def get_items_sheet() -> Sheet:
    rows = get_sheet_data(POKOPIA_ID, "Items")
    _update_trader_schema(rows)

    return Sheet(
        rows,
        id_fields=[ItemFields.ID],
        schema_size=2
    )


@message_guardian(guard)
def get_traders_sheet() -> Sheet:
    rows = get_sheet_data(POKOPIA_ID, "Tradering")
    _update_trader_schema(rows)

    return Sheet(
        rows,
        id_fields=[TraderFields.ID],
        schema_size=2,
        auto_fields=[TraderFields.SORT, TraderFields.RAW_SORT]
    )


def get_ref_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(POKOPIA_ID, "Ref")
    )


def get_db_sheet() -> Sheet:
    return Sheet(
        get_sheet_data(POKOPIA_ID, "DB"),
        schema_size=2,
    )
