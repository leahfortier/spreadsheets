from typing import List, Callable

from util.data import Sheet


class TierSheet:
    def __init__(
            self,
            spreadsheet_id: str,
            id_fields: List[str],
            tiers_tab: str,
            tiers_field: str,
            sort_tab: str,
            rating_field: str,
            new_rank_field: str,
            old_rank_field: str = "",
            diff_field: str = "",
            num_tier_categories: int = 1,
            on_update: Callable[[Sheet, int, List[str]], None] = None,
    ):
        self.spreadsheet_id = spreadsheet_id
        self.id_fields = id_fields

        self.tiers_tab = tiers_tab
        self.tiers_field = tiers_field
        self.num_tier_categories = num_tier_categories

        self.sort_tab = sort_tab
        self.rating_field = rating_field
        self.new_rank_field = new_rank_field
        self.old_rank_field = old_rank_field
        self.diff_field = diff_field

        self.on_update = on_update

