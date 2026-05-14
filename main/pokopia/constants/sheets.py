from enum import Enum

from constants.sheet_id import POKOPIA_ID
from util.data import Sheet
from util.sheets_parse import get_sheet_data
from util.warn import GuardDog, message_guardian


class ItemFields(str, Enum):
    NAME = "game name"
    ID = "serebii name / id"
    SORT_ID = "sort"
    BUY = "buy"
    SELL = "sell"
    TRADE_START = "traders: start"
    TRADE_END = "traders: end"


class TraderFields(str, Enum):
    ID = "id"
    BUY = "add buy"
    SELL = "add sell"


TRADER_PREFIX = "Trader: "

guard = GuardDog()


def get_items_sheet() -> Sheet:
    rows = get_sheet_data(POKOPIA_ID, "Items")
    schema = rows[0]
    helper = rows[1]
    trade_start = schema.index(ItemFields.TRADE_START)
    trade_end = schema.index(ItemFields.TRADE_END)
    for index in range(trade_start + 1, trade_end):
        trader_name = helper[index]
        schema[index] = f'{TRADER_PREFIX}{trader_name}'

    return Sheet(
        rows,
        id_fields=[ItemFields.ID],
        schema_size=2
    )


@message_guardian(guard)
def get_traders_sheet() -> Sheet:
    rows = get_sheet_data(POKOPIA_ID, "Tradering")
    schema = rows[0]
    helper = rows[1]
    for index, trader_name in enumerate(helper):
        if trader_name:
            guard.empty(schema[index])
            schema[index] = f'{TRADER_PREFIX}{trader_name}'

    return Sheet(
        rows,
        id_fields=[TraderFields.ID],
        schema_size=2
    )