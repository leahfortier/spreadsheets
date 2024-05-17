from constants.genshin import get_genshin
from constants.swizzles import get_swizzles
from data import RatingField
from main.constants.sheet_id import L_SWIZZLE_ID, MEL_SWIZZLE_ID
from tierlist import sort_columns, sort_tiers
from swizzles import check_order


def main():
    l_swizzles = get_swizzles(L_SWIZZLE_ID)
    mel_swizzles = get_swizzles(MEL_SWIZZLE_ID)

    l_genshin = get_genshin(
        "L Ranking",
        [
            RatingField("Overall", "Ovrl Rank", "Ovrl +/-"),
            RatingField("Gameplay (Abyss)", "Kit A Rank", "Kit A +/-"),
            RatingField("Gameplay (Casual)", "Kit C Rank", "Kit C +/-"),
            RatingField("Vibe", "Vibe Rank", "Vibe +/-"),
            RatingField("Design Overall", "Dsgn Rank", "Dsgn +/-"),
        ]
    )
    mel_genshin = get_genshin(
        "Mel Ranking",
        [
            RatingField("Overall", "Ovrl Rank", "Ovrl +/-"),
            RatingField("Gameplay", "Kit Rank", "Kit +/-"),
            RatingField("Personality/Lore", "Lore Rank", "Lore +/-"),
            RatingField("Design", "Dsgn Rank", "Dsgn +/-"),
        ]
    )

    # sort_tiers(l_swizzles)
    # sort_tiers(mel_swizzles)
    check_order(l_swizzles)
    # sort_columns(l_genshin)
    # sort_columns(mel_genshin)


main()
