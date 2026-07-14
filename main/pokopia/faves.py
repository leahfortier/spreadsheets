from typing import List, Dict

from terminology import in_yellow

from pokopia.constants.io import SEREBII_FAVES_FILE
from pokopia.constants.sheets import ItemFields, TRADER_PREFIX, NO_FAVE, YES_FAVE
from pokopia.items import Items
from pokopia.ref import Ref
from util.file_io import from_tsv
from util.general import remove_prefix
from util.warn import GuardDog, WarnLevel

guard = GuardDog(level=WarnLevel.ASSERT)


class FaveCategory:
    def __init__(self, fave_name: str, wiki_faves: List[str], items: Items, ref: Ref):
        self.items = items
        self.ref = ref

        self.name = fave_name
        self.wiki_faves: List[str] = wiki_faves

        self.sheet_faves: List[str] = []
        self.sheet_nons: List[str] = []
        for row in items.sheet.rows:
            item_id = items.sheet.get(row, ItemFields.ID)
            fave_value = items.sheet.get(row, fave_name)
            if fave_value == YES_FAVE:
                self.sheet_faves.append(item_id)
            elif fave_value == NO_FAVE:
                self.sheet_nons.append(item_id)
            else:
                guard.empty(fave_value, "Invalid fave value")

        self.traders = []
        for trader_field in items.trader_fields:
            trader_name = remove_prefix(trader_field, TRADER_PREFIX)
            tradermon = ref.db[trader_name]
            if self.name in tradermon.faves:
                self.traders.append(trader_field)

    def _print_trader_map(self, item_id: str):
        item_row = self.items.get(item_id)
        trader_map: Dict[str, List[str]] = {}
        for trader_field in self.traders:
            trader_value = self.items.sheet.get(item_row, trader_field) or "None"
            trader_map.setdefault(trader_value, [])
            trader_map[trader_value].append(trader_field)

        for value, fields in trader_map.items():
            print(f'\t{value}: {fields}')

    def validate(self):
        for item_id in self.sheet_faves:
            if item_id not in self.wiki_faves:
                print(in_yellow(f'{self.name}: {item_id}'))
                self._print_trader_map(item_id)
                pass

        for item_id in self.sheet_nons:
            if item_id in self.wiki_faves:
                # print(in_red(f'{self.name}: {item_id}'))
                # self._print_trader_map(item_id)
                pass

        for item_id in self.wiki_faves:
            if item_id not in self.sheet_faves:
                # print(in_green(f'{self.name}: {item_id}'))
                # self._print_trader_map(item_id)
                pass


class Faves:
    def __init__(self, items: Items, ref: Ref):
        self.items = items

        wiki_rows = from_tsv(SEREBII_FAVES_FILE)
        self.wiki_faves: Dict[str, List[str]] = {}
        for row in wiki_rows:
            # TODO I don't know how to deal with mud right now
            self.wiki_faves[row[0]] = [items.normalize_id(item_id) for item_id in row[1:] if item_id != "Mud"]

        self.faves: Dict[str, FaveCategory] = {}
        for fave_name in items.fave_fields:
            self.faves[fave_name] = FaveCategory(fave_name, self.wiki_faves[fave_name], items, ref)

    def validate(self):
        for fave_name, wiki_faves in self.wiki_faves.items():
            for item_id in wiki_faves:
                item_row = self.items.get(item_id)
                guard.eq(item_id, self.items.sheet.get(item_row, ItemFields.ID))

        for fave in self.faves.values():
            fave.validate()
