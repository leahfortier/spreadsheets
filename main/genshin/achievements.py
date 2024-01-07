from typing import Tuple, Dict, List

from main.genshin.constants.io import WONDERS_INFILE, VERSIONS_OUTFILE, ACHIEVEMENTS_OUTFILE, NAMECARD_INFILE
from main.genshin.constants.sheets import get_achievements_sheet, AchievementFields, ACHIEVEMENT_END, \
    AchievementSections, AchievementCategories
from main.util.data import Sheet
from main.util.file_io import from_tsv, to_tsv
from main.util.general import generic_name


class WikiRow:
    def __init__(self, row: List[str]):
        assert len(row) in [6, 7]
        self.name = row[0].removesuffix(" (Achievement)")
        self.description = row[1]
        self.requirements = row[2]
        self.category = row[-3]
        self.version = row[-2]


class AchievementsWiki:
    def __init__(self, in_file: str, category: AchievementSections, version: str = ""):
        wiki_list = from_tsv(in_file)
        self.version_map: Dict[str, str] = {}
        self.rows: List[WikiRow] = []
        for row in wiki_list:
            if category == AchievementSections.MEMORIES:
                row.insert(-2, AchievementCategories.HANGOUT)
            elif category == AchievementSections.NAMECARD:
                row.insert(-1, version)
                row.insert(-2, AchievementCategories.EXPLORATION)

            wiki_row = WikiRow(row)
            self.rows.append(wiki_row)

            name, version = wiki_row.name, wiki_row.version
            assert self.version_map.get(name, version) == version
            self.version_map[name] = version


class AchievementsSheet:
    def __init__(self):
        self.sheet: Sheet = get_achievements_sheet()

        # Maps from lowercase removed special achievement name to category and index
        self.map: Dict[str, Tuple[str, int]] = {}

        # Maps from category to start and end indices
        self.categories: Dict[str, Tuple[int, int]] = {}
        self.jump_indices = set()
        self.skip_indices = set()

        start_index = 0
        category = ""
        inside = False
        for index, row in enumerate(self.sheet.rows):
            name = self.sheet.get(row, AchievementFields.NAME)

            if name == ACHIEVEMENT_END:
                assert not inside
                break
            elif self.sheet.get(row, AchievementFields.PLAYER_1_MAIN) != "":
                assert inside
                key = generic_name(name)
                # print("'" + key + "'")
                assert key not in self.map
                self.map[key] = (category, index)
            elif "JUMP TO" in name:
                self.jump_indices.add(index)
            else:
                self.skip_indices.add(index)
                if name == AchievementFields.NAME:
                    assert not inside
                    category_row = self.sheet.rows[index - 1]
                    next_category = self.sheet.get(category_row, AchievementFields.NAME)
                    if category != AchievementSections.WONDERS or next_category == AchievementSections.MEMORIES:
                        start_index = index + 1
                        category = next_category
                    inside = True
                elif name == "":
                    assert inside
                    inside = False
                    end_index = index - 1
                    self.categories[category] = (start_index, end_index)

    def has(self, name: str) -> bool:
        return generic_name(name) in self.map

    def get(self, name: str) -> Tuple[str, int]:
        return self.map.get(generic_name(name), (None, None))

    def category(self, name: str) -> str:
        return self.get(name)[0]

    def index(self, name: str) -> int:
        return self.get(name)[1]


def add_version_column(sheet: AchievementsSheet, wiki: AchievementsWiki):
    out = []
    for row in sheet.sheet.rows:
        name = sheet.sheet.get(row, AchievementFields.NAME)
        version = wiki.version_map.get(name, "")
        out.append([version, name])

    to_tsv(VERSIONS_OUTFILE, out)


def new_achievements(sheet: AchievementsSheet, wiki: AchievementsWiki):
    out: List[List[str]] = []

    for row in wiki.rows:
        if not sheet.has(row.name) or sheet.category(row.name) != AchievementSections.WONDERS:
            print(row.version, row.name)
            out_row = [""] * len(sheet.sheet.schema_row)
            sheet.sheet.set(out_row, AchievementFields.NAME, row.name)
            sheet.sheet.set(out_row, AchievementFields.DESCRIPTION, row.description)
            sheet.sheet.set(out_row, AchievementFields.NOTES, row.requirements)
            sheet.sheet.set(out_row, AchievementFields.CATEGORY, row.category)
            sheet.sheet.set(out_row, AchievementFields.VERSION, row.version)
            sheet.sheet.set(out_row, AchievementFields.PLAYER_1_MAIN, "FALSE")
            sheet.sheet.set(out_row, AchievementFields.PLAYER_2_MAIN, "FALSE")
            sheet.sheet.set(out_row, AchievementFields.PLAYER_3_MAIN, "FALSE")

            out.append(out_row)

    to_tsv(ACHIEVEMENTS_OUTFILE, out)


def achievement_order(sheet: AchievementsSheet, wiki: AchievementsWiki):
    start_index, end_index = sheet.categories.get(AchievementSections.WONDERS)
    sheet_index = start_index
    seen = set()

    for wiki_row in wiki.rows:
        wiki_name = generic_name(wiki_row.name)
        if wiki_name in seen:
            continue
        seen.add(wiki_name)

        if sheet_index in sheet.jump_indices:
            sheet_index = sheet.index(wiki_name)
        sheet_row = sheet.sheet.rows[sheet_index]
        sheet_name = generic_name(sheet.sheet.get(sheet_row, AchievementFields.NAME))

        if wiki_name != sheet_name and sheet_name != "sky high":
            print("Order:", wiki_name, sheet_name)
        sheet_index += 1
        while sheet_index in sheet.skip_indices:
            sheet_index += 1


def update_achievements():
    sheet = AchievementsSheet()
    wonders = AchievementsWiki(WONDERS_INFILE, AchievementSections.WONDERS)
    # namecard = AchievementsWiki(NAMECARD_INFILE, AchievementSections.NAMECARD, version="4.2")

    achievement_order(sheet, wonders)

    new_achievements(sheet, wonders)
    # new_achievements(sheet, namecard)

