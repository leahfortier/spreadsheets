from enum import Enum
from typing import List

from constants.sheet_id import POKOPIA_ID
from util.data import Sheet
from util.sheets_parse import get_sheet_data
from util.warn import GuardDog, message_guardian, WarnLevel


class ItemFields(str, Enum):
    NAME = "game name"
    ID = "serebii name / id"
    SORT_ID = "sort"
    PAINT = "paint"
    PAINT_AMOUNT = "amount"
    BUY = "buy"
    SELL = "sell"


class TraderFields(str, Enum):
    ID = "id"
    BUY_FROM = "buy from"
    BUY = "add buy"
    SELL = "add sell"
    PAINT = "add paint"
    PAINT_AMOUNT = "add amt"


class BuyFields(str, Enum):
    SORT = "sort"
    ID = "id"
    BUY = "buy"
    THIS = "this"


TRADE_START = "trade start"
TRADE_END = "trade end"
TRADER_PREFIX = "Trader: "

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
        schema_size=2
    )


def get_buy_sheet() -> Sheet:
    rows = get_sheet_data(POKOPIA_ID, "Buy")
    _update_trader_schema(rows)

    return Sheet(
        rows,
        id_fields=[BuyFields.ID],
        auto_fields=[BuyFields.SORT, BuyFields.BUY],
        schema_size=2
    )