from typing import List, Callable

from util.data import Sheet


class RatingField:
    def __init__(self, rating_field: str, rank_field: str, diff_field: str = None):
        self.rating = rating_field
        self.rank = rank_field
        self.diff = diff_field


class TierSheet:
    def __init__(
            self,
            spreadsheet_id: str,
            id_fields: List[str],
            tiers_tab: str,
            tiers_field: str,
            sort_tab: str,
            rating_fields: List[RatingField],
            dynamic_rank_field: str = None,
            num_tier_categories: int = 1,
            manual_update: Callable[[Sheet, int, List[str]], None] = lambda sheet, output_index, row: None,
    ):
        self.spreadsheet_id = spreadsheet_id
        self.id_fields = id_fields

        self.tiers_tab = tiers_tab
        self.tiers_field = tiers_field
        self.num_tier_categories = num_tier_categories

        self.sort_tab = sort_tab
        self.rating_fields = rating_fields
        self.dynamic_rank_field = dynamic_rank_field

        self.manual_update = manual_update

