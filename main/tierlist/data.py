from typing import List, Callable

from util.data import Sheet


class ShowDiffs:
    def __init__(self, old_rank_field: str, diff_field: str):
        self.old_rank_field = old_rank_field
        self.diff_field = diff_field


class RatingField:
    def __init__(self, rating_field: str, rank_field: str, show_diffs: ShowDiffs = None,):
        self.rating = rating_field
        self.rank = rank_field

        self.show_diffs = show_diffs


class TierSheet:
    def __init__(
            self,
            spreadsheet_id: str,
            id_fields: List[str],
            tiers_tab: str,
            tiers_field: str,
            sort_tab: str,
            rating_fields: List[RatingField],
            num_tier_categories: int = 1,
            # Specific updates can go in here
            on_update: Callable[[Sheet, int, List[str]], None] = None,
    ):
        self.spreadsheet_id = spreadsheet_id
        self.id_fields = id_fields

        self.tiers_tab = tiers_tab
        self.tiers_field = tiers_field
        self.num_tier_categories = num_tier_categories

        self.sort_tab = sort_tab
        self.rating_fields = rating_fields

        self.on_update = on_update or (lambda *args, **kwargs: None)

