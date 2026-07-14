import re
from typing import List, Set, Dict

from terminology import in_green

from main.util.data import Sheet
from pokopia.constants.io import TRADERS_OUTFILE, PAINT_TRADE_OUTFILE, FAVES_OUTFILE
from pokopia.constants.pokes import PAINT_AMOUNTS
from pokopia.constants.sheets import get_items_sheet, ItemFields, get_traders_sheet, TraderFields, TRADER_PREFIX, \
    NO_FAVE, YES_FAVE
from pokopia.ref import Ref
from util.file_io import to_tsv
from util.general import has_prefix, is_number, remove_prefix
from util.warn import GuardDog, message_guardian, WarnLevel

guard = GuardDog(level=WarnLevel.ASSERT)


def get_image_id(item_id: str) -> str:
    return item_id.lower().replace(" ", "").replace("é", "e")


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
        if buy_value == "-":
            guard.empty_or_eq(self.current, buy_value)
            guard.empty(self.buy_vals)
            self.valid_buy = False
        else:
            self.guard_format(buy_value, message)
            self.buy_vals.add(buy_value)

    def get(self) -> str:
        if not self.valid_buy:
            return "-"
        return ", ".join(sorted(self.buy_vals, key=lambda val: int(val.split(" ")[0])))


class Items:
    def __init__(self, ref: Ref):
        self.sheet: Sheet = get_items_sheet()

        self.trader_fields = [field for field in self.sheet.schema if has_prefix(field, TRADER_PREFIX)]
        self.fave_fields = list(ref.favorites)

        self.image_ids: Dict[str, str] = {}
        for row in self.sheet.rows:
            image_id = self.sheet.get(row, ItemFields.IMAGE_ID)
            item_id = self.sheet.get(row, ItemFields.ID)
            self.image_ids[image_id] = item_id

        self.grouped = GroupedItems(self)

    def get(self, item_id: str) -> List[str]:
        return self.sheet.get_row(item_id)

    def normalize_id(self, item_id: str) -> str:
        return self.image_ids[get_image_id(item_id)]

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
                guard.inside(amount, PAINT_AMOUNTS)

            guard.pop_message(item_id)

    def get_buy(self, item_id: str) -> BuyValue:
        row = self.sheet.get_row(item_id)
        current_buy = self.sheet.get(row, ItemFields.BUY)
        return BuyValue(item_id, current_buy)

    def _update_group(self, item_id: str, group: List[str]):
        item_row = self.get(item_id)
        for group_item in group:
            if group_item == item_row:
                continue

            group_row = self.get(group_item)
            for field in self.trader_fields + self.fave_fields:
                item_value = self.sheet.get(item_row, field)
                group_value = self.sheet.get(group_row, field)
                if item_value:
                    guard.empty_or_eq(group_value, item_value, f"Different values for {field} within group")
                    self.sheet.update(group_row, field, item_value)

    def update(self, ref: Ref):
        self.grouped.update()
        
        non_fave_count = 0
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, ItemFields.ID)
            if not item_id:
                continue

            guard.append_message(item_id)

            for trader_field in self.trader_fields:
                trader_value = self.sheet.get(row, trader_field)
                trader_name = remove_prefix(trader_field, TRADER_PREFIX)
                tradermon = ref.db[trader_name]

                guard.append_message(f'{trader_field} {tradermon.faves}')

                if trader_value == NO_FAVE:
                    for fave in tradermon.faves:
                        with message_guardian(guard, fave):
                            current_fave_value = self.sheet.get(row, fave)
                            guard.empty_or_eq(current_fave_value, trader_value)
                            self.sheet.set(row, fave, trader_value)
                            if not current_fave_value:
                                non_fave_count += 1
                elif trader_value == YES_FAVE:
                    fave_values = [self.sheet.get(row, fave) for fave in tradermon.faves]

                    non_no = [fave for fave in tradermon.faves if self.sheet.get(row, fave) != NO_FAVE]
                    guard.bark.nonempty(non_no, "No love left to give")

                    if YES_FAVE in fave_values:
                        pass
                    elif len(non_no) == 1:
                        self.sheet.set(row, non_no[0], trader_value)
                        print(in_green(f'{item_id} - {non_no[0]} ({trader_field})'))
                    else:
                        # print(in_yellow(f'{item_id} - {non_no} ({trader_field})'))
                        pass
                else:
                    guard.empty(trader_value)

                guard.pop_message(f'{trader_field} {tradermon.faves}')

            guard.pop_message(item_id)
        if non_fave_count:
            print(f'{non_fave_count} faves updated')

    def _write_columns(self, filename: str, fields: List[ItemFields | str]):
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
        self._write_columns(TRADERS_OUTFILE, self.trader_fields)

    def write_faves(self):
        self._write_columns(FAVES_OUTFILE, self.fave_fields)


class Traders:
    def __init__(self):
        self.sheet: Sheet = get_traders_sheet()
        self.trader_fields = [field for field in self.sheet.schema if has_prefix(field, TRADER_PREFIX)]

        for row in self.sheet.rows:
            item_id = self.sheet.get(row, TraderFields.ID)
            if not item_id:
                continue

            guard.append_message(item_id)

            add_paint = self.sheet.get(row, TraderFields.PAINT)
            add_amount = self.sheet.get(row, TraderFields.PAINT_AMOUNT)
            if add_paint == "-":
                guard.empty_or_eq(add_amount, "-")
                add_amount = "-"
            elif add_paint:
                guard.inside(add_amount, [""] + PAINT_AMOUNTS)
                if not add_amount:
                    add_amount = "1"
            self.sheet.update(row, TraderFields.PAINT_AMOUNT, add_amount)

            guard.pop_message(item_id)

    @message_guardian(guard, "Traders.update")
    def update(self, items: Items):
        freq: Dict[str, int] = {}
        for row in self.sheet.rows:
            item_id = self.sheet.get(row, TraderFields.ID)
            if not item_id:
                continue

            guard.append_message(item_id)
            item_row = items.sheet.get_row(item_id)

            def update_field(add_field: TraderFields | str, current_field: ItemFields | str):
                add_value = self.sheet.get(row, add_field)
                current_value = items.sheet.get(item_row, current_field)
                if add_value:
                    guard.empty_or_eq(current_value, add_value)
                    items.sheet.set(item_row, current_field, add_value)
                    if not current_value:
                        freq.setdefault(current_field, 0)
                        freq[current_field] += 1

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

            guard.pop_message(item_id)

        for field, count in freq.items():
            print(f'{count} values updated for {field}')


# Items should be considered "grouped" if expected to share all fave attributes
class GroupedItems:
    def __init__(self, items: Items):
        self.items = items

        self.cds = []
        self.fossils = []
        self.slates = []
        self.paints = []
        self.paint_balloons = []
        self.fireworks = []
        self.wallpaper = []
        self.meteor_lamps = []
        self.music_mats = []

        self.groups = [
            self.cds, self.fossils, self.slates, self.paints, self.paint_balloons,
            self.fireworks, self.wallpaper, self.meteor_lamps, self.music_mats
        ]

        for row in items.sheet.rows:
            item_id = items.sheet.get(row, ItemFields.ID)
            if not item_id:
                continue

            raw_storage = items.sheet.get(row, ItemFields.STORAGE)
            storage = set(raw_storage.split(","))

            def append_if(group: List[str], condition: bool):
                if condition:
                    group.append(item_id)

            append_if(self.cds, "CDs" in storage)
            append_if(self.fossils, "Fossils" in storage)
            append_if(self.slates, "Slates" in storage)
            append_if(self.paints, "Base Paint" in storage)
            append_if(self.paint_balloons, "Paint Balloons" in storage)
            append_if(self.fireworks, "Fireworks" in storage)
            append_if(self.wallpaper, "Wallpaper" in storage)
            append_if(self.meteor_lamps, "meteor lamp" in item_id)
            append_if(self.music_mats, "Music mat" in item_id)

    def _update_group(self, item_id: str, group: List[str]):
        item_row = self.items.get(item_id)
        for group_item in group:
            if group_item == item_row:
                continue

            group_row = self.items.get(group_item)
            for field in self.items.trader_fields + self.items.fave_fields:
                item_value = self.items.sheet.get(item_row, field)
                group_value = self.items.sheet.get(group_row, field)
                if item_value:
                    guard.empty_or_eq(group_value, item_value, f"Different values for {field} within group")
                    self.items.sheet.update(group_row, field, item_value)

    def update(self):
        for row in self.items.sheet.rows:
            item_id = self.items.sheet.get(row, ItemFields.ID)
            if not item_id:
                continue

            guard.append_message(item_id)

            for group in self.groups:
                if item_id in group:
                    self._update_group(item_id, group)
