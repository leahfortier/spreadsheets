from constants.swizzles import get_swizzles
from tierlist import sort_tiers, sort_columns
from main.constants.sheet_id import L_SWIZZLE_ID, MEL_SWIZZLE_ID
from constants.genshin import get_genshin
from data import RatingField, ShowDiffs


def main():
    l_swizzles = get_swizzles(L_SWIZZLE_ID)
    mel_swizzles = get_swizzles(MEL_SWIZZLE_ID)

    l_genshin = get_genshin(
        "L Ranking",
        [
            RatingField("Overall", "Ovrall Rank"),
            RatingField("Gameplay (Abyss)", "Kit (A) Rank"),
            RatingField("Gameplay (Casual)", "Kit (C) Rank"),
            RatingField("Personality", "Pers. Rank"),
            RatingField("Lore", "Lore Rank"),
            RatingField("Design Overall", "Curr Rank", show_diffs=ShowDiffs(
                old_rank_field="Design Rank",
                diff_field="+/-",
            )),
        ]
    )
    mel_genshin = get_genshin(
        "Mel Ranking",
        [
            RatingField("Overall", "Ovrall Rank"),
            RatingField("Gameplay", "Kit Rank"),
            RatingField("Personality/Lore", "Lore Rank"),
            RatingField("Design", "Design Rank"),
        ]
    )

    # sort_tiers(l_swizzles)
    # sort_tiers(mel_swizzles)
    sort_columns(l_genshin)
    # sort_columns(mel_genshin)


main()
