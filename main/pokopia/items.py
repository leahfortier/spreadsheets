import re
from typing import List, Set

from main.util.data import Sheet
from pokopia.constants.io import TRADERS_OUTFILE, PAINT_TRADE_OUTFILE, BUY_FROM_OUTFILE
from pokopia.constants.sheets import get_items_sheet, ItemFields, get_traders_sheet, TraderFields, TRADER_PREFIX, \
    TRADE_END, TRADE_START, get_buy_sheet, BuyFields
from util.file_io import to_tsv
from util.general import has_prefix, is_number
from util.warn import GuardDog, message_guardian, WarnLevel

guard = GuardDog(level=WarnLevel.ASSERT)


def guard_buy_format(buy_value: str, message: str = None):
    if not is_number(buy_value):
        guard.truthy(re.fullmatch("\\d+ \\(:\\d+\\)", buy_value), message)


class BuyValue:
    def __init__(self, item_id: str, current_buy: str):
        self.item_id = item_id
        self.current = current_buy
        self.valid_buy = current_buy != "-"

        self.buy_vals: Set[str] = set()
        if current_buy and self.valid_buy:
            for split_val in current_buy.split(", "):
                self.add(split_val, "current split: " + current_buy)

    def guard_format(self, buy_value: str, message: str = None):
        with message_guardian(guard, self.item_id):
            guard_buy_format(buy_value, message)

    def add(self, buy_value: str, message: str = None):
        self.guard_format(buy_value, message)
        self.buy_vals.add(buy_value)

    def get(self) -> str:
        if not self.valid_buy:
            return self.current
        return ", ".join(sorted(self.buy_vals, key=lambda val: int(val.split(" ")[0])))


class Items:
    def __init__(self):
        self.sheet: Sheet = get_items_sheet()

    @message_guardian(guard)
    def validate(self):
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, ItemFields.ID)
            guard.append_message(item_id)

            paint = self.sheet.get(row, ItemFields.PAINT)
            amount = self.sheet.get(row, ItemFields.PAINT_AMOUNT)
            if paint == "-":
                guard.eq(amount, "-")
            elif paint == "":
                guard.eq(amount, "")
            else:
                guard.inside(amount, ["1", "10"])

            guard.pop_message(item_id)

    def get_buy(self, item_id: str) -> BuyValue:
        row = self.sheet.get_row(item_id)
        current_buy = self.sheet.get(row, ItemFields.BUY)
        return BuyValue(item_id, current_buy)

    def _write_columns(self, filename: str, fields: List[ItemFields]):
        out_rows = [
            [self.sheet.get(row, field) for field in fields]
            for row in self.sheet.rows
        ]
        to_tsv(filename, out_rows)

    def write_paint_trade_values(self):
        self._write_columns(
            PAINT_TRADE_OUTFILE,
            [ItemFields.PAINT, ItemFields.PAINT_AMOUNT, ItemFields.BUY, ItemFields.SELL]
        )

    def write_traders(self):
        trade_start = self.sheet.schema[TRADE_START]
        trade_end = self.sheet.schema[TRADE_END]
        out_rows = [row[trade_start+1:trade_end] for row in self.sheet.rows]
        to_tsv(TRADERS_OUTFILE, out_rows)


class BuyFrom:
    def __init__(self):
        self.sheet: Sheet = get_buy_sheet()
        self.trader_fields = [field for field in self.sheet.schema if has_prefix(field, TRADER_PREFIX)]

    def get_item(self, item_id: str) -> List[str]:
        if self.sheet.has_id(item_id):
            return self.sheet.get_row(item_id)

        new_row = self.sheet.add_row()
        self.sheet.update(new_row, BuyFields.ID, item_id)
        return new_row

    @message_guardian(guard)
    def update_trader(self, item_id: str, buy_from: str, buy_value: str):
        guard_buy_format(buy_value)

        row = self.get_item(item_id)
        traders = buy_from.split(", ")
        for trader in traders:
            with message_guardian(guard, trader):
                trader_field = TRADER_PREFIX + trader
                current_value = self.sheet.get(row, trader_field)
                guard.empty_or_eq(current_value, buy_value)
                self.sheet.update(row, trader_field, buy_value)

    def update(self, items: Items):
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, BuyFields.ID)
            guard.append_message(item_id)

            buy_value = items.get_buy(item_id)
            for trader in self.trader_fields:
                trade_val = self.sheet.get(row, trader)
                if trade_val:
                    buy_value.add(trade_val)
            this_buy = buy_value.get()
            self.sheet.update(row, BuyFields.THIS, this_buy)

            guard.pop_message(item_id)

    def write(self):
        to_tsv(BUY_FROM_OUTFILE, self.sheet.rows)


class Traders:
    def __init__(self):
        self.sheet: Sheet = get_traders_sheet()
        self.trader_fields = [field for field in self.sheet.schema if has_prefix(field, TRADER_PREFIX)]

        for row in self.sheet.rows:
            add_paint = self.sheet.get(row, TraderFields.PAINT)
            add_amount = self.sheet.get(row, TraderFields.PAINT_AMOUNT)
            if add_paint == "-":
                guard.empty_or_eq(add_amount, "-")
                add_amount = "-"
            elif add_paint:
                guard.inside(add_amount, ["", "1", "10"])
                if not add_amount:
                    add_amount = "1"
            self.sheet.update(row, TraderFields.PAINT_AMOUNT, add_amount)

    @message_guardian(guard, "Traders.update")
    def update(self, items: Items, buy_sheet: BuyFrom):
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, TraderFields.ID)
            if item_id == "":
                continue

            guard.append_message(item_id)
            item_row = items.sheet.get_row(item_id)

            def update_field(add_field: TraderFields | str, current_field: ItemFields | str):
                add_value = self.sheet.get(row, add_field)
                current_value = items.sheet.get(item_row, current_field)
                if add_value:
                    guard.empty_or_eq(current_value, add_value)
                    items.sheet.update(item_row, current_field, add_value)

            buy_value = items.get_buy(item_id)
            add_buy = self.sheet.get(row, TraderFields.BUY)
            if add_buy:
                buy_value.add(add_buy)
                items.sheet.update(item_row, ItemFields.BUY, buy_value.get())
            update_field(TraderFields.SELL, ItemFields.SELL)

            update_field(TraderFields.PAINT, ItemFields.PAINT)
            update_field(TraderFields.PAINT_AMOUNT, ItemFields.PAINT_AMOUNT)

            for trader in self.trader_fields:
                with message_guardian(guard, trader):
                    update_field(trader, trader)

            buy_from = self.sheet.get(row, TraderFields.BUY_FROM)
            if buy_from:
                buy_sheet.update_trader(item_id, buy_from, add_buy or buy_value.get())

            guard.pop_message(item_id)



