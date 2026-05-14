from typing import List, Dict

from main.util.data import Sheet
from pokopia.constants.io import TRADERS_OUTFILE, TRADE_VALUE_OUTFILE
from pokopia.constants.sheets import get_items_sheet, ItemFields, get_traders_sheet, TraderFields, TRADER_PREFIX
from util.file_io import to_tsv
from util.general import has_prefix, is_empty
from util.warn import GuardDog, message_guardian

guard = GuardDog()


class Items:
    def __init__(self):
        self.sheet: Sheet = get_items_sheet()
        self.items: Dict[str, List[str]] = {}
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, ItemFields.ID)
            guard.nonside(item_id, self.items)
            self.items[item_id] = row

    def write_trade_value(self):
        out_rows = [
            [self.sheet.get(row, ItemFields.BUY), self.sheet.get(row, ItemFields.SELL)]
            for row in self.sheet.rows
        ]
        to_tsv(TRADE_VALUE_OUTFILE, out_rows)

    def write_traders(self):
        trade_start = self.sheet.schema[ItemFields.TRADE_START]
        trade_end = self.sheet.schema[ItemFields.TRADE_END]
        out_rows = [row[trade_start+1:trade_end] for row in self.sheet.rows]
        to_tsv(TRADERS_OUTFILE, out_rows)


class SellValue:
    def __init__(self):
        self.first = ""
        self.second = ""

    @message_guardian(guard)
    def add(self, value: str):
        if not value:
            return
        guard.append_message(value)

        # input value must have exactly one "/"
        guard.kill.eq(value.count("/"), 1)
        if value.endswith("/"):
            first = str(int(value.rstrip("/")))
            guard.kill.empty_or_eq(self.first, first)
            self.first = first
        elif value.startswith("/"):
            second = str(int(value.lstrip("/")))
            guard.kill.empty_or_eq(self.second, second)
            self.second = second
        else:
            split = value.split("/")
            guard.kill.eq(len(split), 2)
            first = str(int(split[0]))
            second = str(int(split[1]))
            guard.kill.empty_or_eq(self.first, first)
            guard.kill.empty_or_eq(self.second, second)
            self.first = first
            self.second = second

    def __str__(self):
        guard.kill.sniff(self.first or self.second)
        return f'{self.first}/{self.second}'


def get_sell_value(current_sell: str, add_sell: str) -> str:
    sell_value = SellValue()
    sell_value.add(current_sell)
    sell_value.add(add_sell)
    return str(sell_value)


class Traders:
    def __init__(self):
        self.sheet: Sheet = get_traders_sheet()
        self.trader_fields = [field for field in self.sheet.schema if has_prefix(field, TRADER_PREFIX)]

    @message_guardian(guard)
    def update(self, items: Items):
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, TraderFields.ID)
            if item_id == "":
                continue

            guard.append_message(item_id)
            add_buy = self.sheet.get(row, TraderFields.BUY)
            add_sell = self.sheet.get(row, TraderFields.SELL)

            item_row = items.items[item_id]
            current_buy = items.sheet.get(item_row, ItemFields.BUY)
            current_sell = items.sheet.get(item_row, ItemFields.SELL)

            if add_buy:
                guard.kill.empty_or_eq(current_buy, add_buy)
                items.sheet.update(item_row, ItemFields.BUY, add_buy)

            if add_sell:
                sell_value = get_sell_value(current_sell, add_sell)
                items.sheet.update(item_row, ItemFields.SELL, sell_value)

            for trader in self.trader_fields:
                guard.append_message(trader)
                trade_value = self.sheet.get(row, trader)
                if trade_value:
                    current_value = items.sheet.get(item_row, trader)
                    guard.kill.empty_or_eq(current_value, trade_value)
                    items.sheet.update(item_row, trader, trade_value)
                guard.pop_message(trader)

            guard.pop_message(item_id)



