from typing import List

from main.constants.sheet_id import GENSHIN_RANKING_ID
from constants.sheets import TierSheet
from util.data import Sheet

IMAGE_PATH_MAP = {
    "Albedo": "3/30/",
    "Alhaitham": "2/2c/",
    "Aloy": "e/e5/",
    "Amber": "7/75/",
    "Arlecchino": "9/9a/",
    "Ayaka": "5/51/",
    "Ayato": "2/27/",
    "Baizhu": "c/cb/",
    "Barbara": "6/6a/",
    "Beidou": "e/e1/",
    "Bennett": "7/79/",
    "Candace": "d/dd/",
    "Charlotte": "d/d2/",
    "Chevreuse": "8/8a/",
    "Childe": "8/85/",
    "Chiori": "8/88/",
    "Chongyun": "3/35/",
    "Collei": "a/a2/",
    "Cyno": "3/31/",
    "Dehya": "3/3f/",
    "Diluc": "3/3d/",
    "Diona": "4/40/",
    "Dori": "5/54/",
    "Eula": "a/af/",
    "Faruzan": "b/b2/",
    "Fischl": "9/9a/",
    "Freminet": "e/ee/",
    "Furina": "e/e6/",
    "Gaming": "7/77/",
    "Ganyu": "7/79/",
    "Gorou": "f/fe/",
    "Heizou": "2/20/",
    "Hu Tao": "e/e9/",
    "Itto": "7/7b/",
    "Jean": "6/64/",
    "Kaeya": "b/b6/",
    "Kaveh": "1/1f/",
    "Kazuha": "e/e3/",
    "Keqing": "5/52/",
    "Kirara": "b/b6/",
    "Klee": "9/9c/",
    "Kokomi": "f/ff/",
    "Kujou Sara": "d/df/",
    "Layla": "1/1a/",
    "Lisa": "6/65/",
    "Lynette": "a/ad/",
    "Lyney": "b/b2/",
    "Mika": "d/dd/",
    "Mona": "4/41/",
    "Nahida": "f/f9/",
    "Navia": "c/c0/",
    "Neuvillette": "2/21/",
    "Nilou": "5/58/",
    "Ningguang": "e/e0/",
    "Noelle": "8/8e/",
    "Qiqi": "b/b3/",
    "Raiden Shogun": "2/24/",
    "Razor": "b/b8/",
    "Rosaria": "3/35/",
    "Sayu": "2/22/",
    "Shenhe": "a/af/",
    "Shinobu": "b/b3/",
    "Sucrose": "0/0e/",
    "Thoma": "5/5b/",
    "Tighnari": "8/87/",
    "Traveler": "5/59/",
    "Venti": "f/f1/",
    "Wanderer": "f/f8/",
    "Wriothesley": "b/bb/",
    "Xiangling": "3/39/",
    "Xianyun": "d/d3/",
    "Xiao": "f/fd/",
    "Xingqiu": "d/d4/",
    "Xinyan": "2/24/",
    "Yae Miko": "b/ba/",
    "Yanfei": "5/54/",
    "Yaoyao": "8/83/",
    "Yelan": "d/d3/",
    "Yoimiya": "8/88/",
    "Yun Jin": "9/9c/",
    "Zhongli": "a/a6/",
}

IMAGE_NAME_MAP = {
    "Ayaka": "Kamisato Ayaka",
    "Ayato": "Kamisato Ayato",
    "Childe": "Tartaglia",
    "Heizou": "Shikanoin Heizou",
    "Itto": "Arataki Itto",
    "Kazuha": "Kaedehara Kazuha",
    "Kokomi": "Sangonomiya Kokomi",
    "Shinobu": "Kuki Shinobu",
}

NAME_FIELD = "Character"
ICON_FIELD = "Icon"


def update_genshin(sheet: Sheet, index: int, row: List[str]) -> None:
    name = sheet.get(row, NAME_FIELD)

    unique_path = IMAGE_PATH_MAP[name]
    url_name = name
    if name in IMAGE_NAME_MAP:
        url_name = IMAGE_NAME_MAP[name]
    url_name = url_name.replace(" ", "_")

    # YES this does say genshin instead of genshin and it's driving me crazy
    # https://static.wikia.nocookie.net/gensin-impact/images/0/0e/Sucrose_Icon.png/revision/latest/scale-to-width-down/50?cb=20210213163209
    image_url = (f'https://static.wikia.nocookie.net/gensin-impact/images/{unique_path}'
                 f'{url_name}_Icon.png/revision/latest?format=original')

    icon_formula = f'=IMAGE("{image_url}")'
    sheet.update(row, ICON_FIELD, icon_formula, print_diff=False)

    gallery_url = f'https://genshin-impact.fandom.com/wiki/{url_name}/Gallery'
    url_formula = f'=HYPERLINK("{gallery_url}", "{name}")'
    sheet.update(row, NAME_FIELD, url_formula, print_diff=False)


GENSHIN: TierSheet = TierSheet(
    spreadsheet_id=GENSHIN_RANKING_ID,
    id_fields=[NAME_FIELD],
    tiers_tab="Template",
    tiers_field="Tiers",
    sort_tab="L Ranking",
    rating_field="Design Overall",
    new_rank_field="Design Rank",
    num_tier_categories=2,
    on_update=update_genshin,
)
