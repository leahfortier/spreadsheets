from typing import Tuple, Dict, List, Optional

from main.genshin.constants.io import ACHIEVEMENTS_INFILE, VERSIONS_OUTFILE
from main.genshin.constants.sheets import get_achievements_sheet, AchievementFields, ACHIEVEMENT_END
from main.util.data import Sheet
from main.util.file_io import from_tsv, to_tsv
from main.util.general import generic_name, remove_suffix


class WikiRow:
    def __init__(self, row: List[str]):
        assert len(row) in [6, 7]
        self.name = row[0]
        self.version = row[-2]


class AchievementsWiki:
    def __init__(self):
        wiki_list = from_tsv(ACHIEVEMENTS_INFILE)
        self.version_map: Dict[str, str] = {}
        self.rows: List[WikiRow] = []
        for row in wiki_list:
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
        self.skip_indices = set()

        start_index = 0
        category = ""
        inside = False
        for index, row in enumerate(self.sheet.rows):
            name = self.sheet.get(row, AchievementFields.NAME)
            if name == ACHIEVEMENT_END:
                assert not inside
                break
            elif name == AchievementFields.NAME:
                assert not inside
                start_index = index + 1
                category_row = self.sheet.rows[start_index - 2]
                category = self.sheet.get(category_row, AchievementFields.NAME)
                inside = True
            elif name == "":
                assert inside
                end_index = index - 1
                inside = False
                self.categories[category] = (start_index, end_index)
            elif self.sheet.get(row, AchievementFields.PLAYER_1_MAIN) != "":
                assert inside
                self.map[generic_name(name)] = (category, index)
            else:
                self.skip_indices.add(index)

    def get_row(self, name: str) -> Optional[List[str]]:
        name = generic_name(name)
        if name in self.map:
            category, index = self.map.get(name)
            return self.sheet.rows[index]
        return None


def add_version_column():
    wiki = AchievementsWiki()
    sheet = AchievementsSheet()

    out = []
    for row in sheet.sheet.rows:
        name = sheet.sheet.get(row, AchievementFields.NAME)
        version = wiki.version_map.get(name, "")
        out.append([version, name])

    to_tsv(VERSIONS_OUTFILE, out)


def update_achievements():
    wiki = AchievementsWiki()
    sheet = AchievementsSheet()

    out_row: List[str] = []

    for row in wiki.rows:
        name, version = row.name, row.version
        name = remove_suffix(name, [" (Achievement)"])
        if not sheet.get_row(name):
            print(name, version)


