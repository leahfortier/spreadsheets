from typing import List, Dict

from constants.swizzles import ERAS, ERA_FIELD, TITLE_FIELD
from data import TierSheet
from tierlist import get_tiers
from util.data import Sheet
from util.sheets_parse import get_sheet_data


class Swizzle:
    def __init__(self, config: TierSheet):
        self.config = config

        self.tiers = get_tiers(config.spreadsheet_id, config.tiers_tab, config.tiers_field, config.num_tier_categories)
        self.discography = Sheet(get_sheet_data(config.spreadsheet_id, config.sort_tab), id_fields=config.id_fields)

        self.eras: Dict[str, Sheet] = {}
        for era in ERAS:
            era_tab = "Era - " + era
            era_sheet = Sheet(get_sheet_data(config.spreadsheet_id, era_tab))
            self.eras[era] = era_sheet

    def era_order(self, era: str) -> List[str]:
        order = []
        sheet = self.eras[era]
        for row in sheet.rows:
            # Title is the first column
            order.append(row[0])
        return order

    def disc_order(self, era: str) -> List[str]:
        order = []
        sheet = self.discography
        for row in sheet.rows:
            if sheet.get(row, ERA_FIELD).startswith(era):
                order.append(sheet.get(row, TITLE_FIELD))

        return order


def check_order(config: TierSheet):
    swizzle = Swizzle(config)
    for era in ERAS:
        era_order = swizzle.era_order(era)
        disc_order = swizzle.disc_order(era)
        assert len(era_order) == len(disc_order)
        if era_order != disc_order:
            print(f"Out of order for {era}:")
            for i, (era_title, disc_title) in enumerate(zip(era_order, disc_order)):
                if era_title != disc_title:
                    print(f"\t{i + 1} {era_title} (Era), {disc_title} (Discography)")
