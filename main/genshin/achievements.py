from typing import Dict, List, Set

from main.genshin.constants.io import WONDERS_INFILE, VERSIONS_OUTFILE, NAMECARD_INFILE, \
    MEMORIES_INFILE
from main.genshin.constants.sheets import AchievementFields, ACHIEVEMENT_END, \
    AchievementSections, AchievementCategories, Tab, get_sheet, PLAYER_FIELDS
from main.util.data import Sheet
from main.util.file_io import from_tsv, to_tsv
from main.util.general import generic_name, remove_prefix
from util.warn import GuardDog

guard = GuardDog()


class WikiRow:
    def __init__(self, row: List[str]):
        guard.kill.inside(len(row), [6, 7], str(row))
        self.name = row[0].removesuffix(" (Achievement)")
        self.description = row[1]
        self.requirements = row[2]
        self.category = row[-3]
        self.version = row[-2]

        self.key = generic_name(self.name)


class AchievementsWiki:
    def __init__(self, in_file: str, category: AchievementSections, version: str = ""):
        wiki_list = from_tsv(in_file)
        self.version_map: Dict[str, str] = {}
        self.rows: List[WikiRow] = []
        for row in wiki_list:
            if not row:
                continue

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


class Achievement:
    def __init__(self, sheet: Sheet, row: List[str], category: str, index: int):
        self.name = sheet.get(row, AchievementFields.ACHIEVEMENT)
        self.version = float(sheet.get(row, AchievementFields.VERSION))

        self.category = category
        self.sheet_index = index

        self.key = generic_name(self.name)

        self.category_index = None
        self.category_index: int

        self.count = 0
        for field in PLAYER_FIELDS[0]:
            checkbox = sheet.get(row, field)
            if checkbox:
                self.count += 1

    def set_row_index(self, index: int):
        self.category_index = index


class Category:
    def __init__(self, name: str, start_index: int, end_index: int):
        self.name = name
        self.start_index = start_index
        self.end_index = end_index

        self.key = generic_name(self.name)

        self.rows: List[Achievement] = []
        self.total = 0

    def add(self, achievement: Achievement):
        achievement.set_row_index(len(self.rows))
        self.rows.append(achievement)
        self.total += achievement.count

class AchievementsSheet:
    def __init__(self):
        self.sheet: Sheet = get_sheet(Tab.ACHIEVEMENTS)

        self.map: Dict[str, Achievement] = {}
        self.categories: Dict[str, Category] = {}
        self.wonder_categories: List[Category] = []

        # Index to category
        self.jump_map: Dict[int, str] = {}
        self.skip_indices: Set[int] = set()

        self._read_sheet()
        self._set_categories()

    def has(self, name: str) -> bool:
        return generic_name(name) in self.map

    def get(self, name: str) -> Achievement:
        return self.map.get(generic_name(name))

    def category(self, name: str) -> Category:
        return self.categories[name]

    def wonder_category(self, name: str) -> Category:
        for category in self.wonder_categories:
            if name in [category.name, category.key]:
                return category

    def get_wonder(self, index: int) -> Category:
        for category in self.wonder_categories:
            if category.start_index <= index < category.end_index:
                return category

    def index(self, name: str) -> int:
        return self.get(name).sheet_index

    def _set_categories(self):
        wonder = self.category(AchievementSections.WONDERS)
        for category in self.categories.values():
            if category == wonder:
                continue

            for index in range(category.start_index, category.end_index):
                guard.bark.nonside(index, self.jump_map, "Jump map is only for wonders!")
                if index in self.skip_indices:
                    continue

                row = self.sheet.rows[index]
                name = self.sheet.get(row, AchievementFields.ACHIEVEMENT)
                achievement = self.get(name)
                category.add(achievement)

        wonder_index_map: Dict[str, int] = {
            category.key: category.start_index
            for category in self.wonder_categories
        }
        index = wonder.start_index
        current_category: Category = None
        seen: Set[str] = set()
        while index < wonder.end_index:
            if index in self.jump_map:
                jump_category = self.jump_map[index]
                guard.kill.inside(current_category.key, wonder_index_map, f"Invalid wonder category")
                guard.kill.uneq(jump_category, current_category.key, f"Invalid jump category {index}")

                wonder_index_map[current_category.key] = index + 1
                index = wonder_index_map[jump_category]
            elif index in self.skip_indices:
                index += 1
            else:
                current_category = self.get_wonder(index)
                assert current_category, str(index)

                # Check if we've already started this category and if we're already past it
                jump_index = wonder_index_map[current_category.key]
                if jump_index > index:
                    index = jump_index
                    continue

                row = self.sheet.rows[index]
                name = self.sheet.get(row, AchievementFields.ACHIEVEMENT)
                achievement = self.get(name)

                guard.nonside(achievement.key, seen, "Duplicate achievement")
                seen.add(achievement.key)

                current_category.add(achievement)
                wonder.add(achievement)

                index += 1

    def _read_sheet(self):
        start_index = 0
        current_category = ""
        wonder_index = 0
        wonder_sub = ""
        inside = False
        for index, row in enumerate(self.sheet.rows):
            name = self.sheet.get(row, AchievementFields.ACHIEVEMENT)

            if name == ACHIEVEMENT_END:
                assert not inside
                break
            elif self.sheet.get(row, AchievementFields.PLAYER_MAIN) != "":
                assert inside
                achievement = Achievement(self.sheet, row, current_category, index)
                guard.nonside(achievement.key, self.map, "Duplicate achievement")
                self.map[achievement.key] = achievement
            elif "JUMP TO" in name:
                jump_category = generic_name(remove_prefix(name.lstrip("↓↑ "), "JUMP TO"))
                self.jump_map[index] = jump_category
            else:
                self.skip_indices.add(index)
                if name == AchievementFields.ACHIEVEMENT:
                    assert not inside
                    category_row = self.sheet.rows[index - 1]
                    next_category = self.sheet.get(category_row, AchievementFields.ACHIEVEMENT)
                    if current_category == AchievementSections.WONDERS and next_category != AchievementSections.MEMORIES:
                        wonder_index = index + 1
                        wonder_sub = next_category
                    else:
                        start_index = index + 1
                        current_category = next_category
                        wonder_sub = None
                    inside = True
                elif name == "":
                    assert inside
                    inside = False
                    end_index = index
                    self.categories[current_category] = Category(current_category, start_index, end_index)
                    if current_category == AchievementSections.WONDERS:
                        if wonder_sub:
                            self.wonder_categories.append(Category(wonder_sub, wonder_index, end_index))
                        else:
                            self.wonder_categories.append(Category(current_category, start_index, end_index))


def add_version_column(sheet: AchievementsSheet, wiki: AchievementsWiki):
    out = []
    for row in sheet.sheet.rows:
        name = sheet.sheet.get(row, AchievementFields.ACHIEVEMENT)
        version = wiki.version_map.get(name, "")
        out.append([version, name])

    to_tsv(VERSIONS_OUTFILE, out)


def new_achievements(sheet: AchievementsSheet, wiki: AchievementsWiki):
    for row in wiki.rows:
        if not sheet.has(row.name):
            print("Missing:", row.version, row.name)


def achievement_order(sheet: AchievementsSheet, wiki: AchievementsWiki):
    wonder = sheet.categories.get(AchievementSections.WONDERS)
    wonder_rows: List[Achievement] = wonder.rows.copy()

    seen = set()

    disagrees = [
        ("sky high", 1),
        ("the final fonta sea", 3)
    ]

    for key, shift in disagrees:
        achievement = sheet.get(key)
        index = achievement.category_index

        guard.eq(achievement.category, AchievementSections.WONDERS, "Disagree category")
        guard.eq(wonder_rows[index], achievement, "Disagree index")

        wonder_rows.insert(index + shift, wonder_rows.pop(index))

    sheet_index = 0
    for wiki_row in wiki.rows:
        wiki_name = wiki_row.key
        if wiki_name in seen:
            continue
        seen.add(wiki_name)

        achievement = wonder_rows[sheet_index]
        guard.info.eq(wiki_name, achievement.key, "Order")
        sheet_index += 1


def update_achievements():
    sheet = AchievementsSheet()
    wonders = AchievementsWiki(WONDERS_INFILE, AchievementSections.WONDERS)
    memories = AchievementsWiki(MEMORIES_INFILE, AchievementSections.MEMORIES)
    namecard = AchievementsWiki(NAMECARD_INFILE, AchievementSections.NAMECARD, version="4.2")

    achievement_order(sheet, wonders)

    new_achievements(sheet, wonders)
    new_achievements(sheet, memories)
    new_achievements(sheet, namecard)

