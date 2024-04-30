from typing import List

from data import RatingField, TierSheet

from main.constants.sheet_id import GENSHIN_RANKING_ID


def get_genshin(sort_tab: str, rating_fields: List[RatingField]) -> TierSheet:
    return TierSheet(
        spreadsheet_id=GENSHIN_RANKING_ID,
        id_fields=["Character"],
        tiers_tab="Template",
        tiers_field="Tiers",
        sort_tab=sort_tab,
        rating_fields=rating_fields,
        dynamic_rank_field="Curr Rank",
        num_tier_categories=2,
    )
