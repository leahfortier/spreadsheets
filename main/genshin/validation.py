from typing import Set, List, Dict, Self

from genshin.achievements import AchievementsSheet
from genshin.characters import CharacterSheet, CharacterRow
from genshin.constants.sheets import get_sheet, Tab, BuildsFields, BUILD_TABS, WeaponMethod, BUILD_SORT_FIELDS, \
    AchievementSections
from util.data import Sheet
from util.warn import GuardDog, message_guardian

guard: GuardDog = GuardDog()


@message_guardian(guard)
def get_values(tab_name: Tab, field_name: str) -> Set[str]:
    guard.append_message(tab_name + " " + field_name)
    values = set()
    sheet: Sheet = get_sheet(tab_name)
    for row in sheet.rows:
        value = sheet.get(row, field_name)
        # If this fails with multiple values, there are likely hidden empty rows after the values
        # that need to be deleted instead of hidden
        guard.bark.truthy(value)
        values.add(value)
    return values


@message_guardian(guard)
def validate_character_data(characters: CharacterSheet):
    trounces = get_values(Tab.TROUNCES, "Drop")
    boss_drops = get_values(Tab.BOSS_DROPS, "Material")
    enemy_drops = get_values(Tab.ENEMY_DROPS, "Material")
    specialties = get_values(Tab.LOCALS, "Specialty")
    recipes = get_values(Tab.RECIPES, "Recipe")
    recipes.add("None")

    for character in characters.rows:
        if character.name.endswith("Traveler"):
            continue

        guard.append_message(character.name)

        def check_asset(asset: str, values: Set[str]):
            guard.inside(asset, values)

        check_asset(character.trounce, trounces)
        check_asset(character.boss_mat, boss_drops)
        check_asset(character.enemy_mat, enemy_drops)
        check_asset(character.local, specialties)
        check_asset(character.recipe, recipes)

        guard.pop_message(character.name)


@message_guardian(guard)
def validate_talents(sheet: Sheet, row: List[str], character: CharacterRow):
    constellation = int(sheet.get(row, BuildsFields.CONSTELLATION))
    normal = sheet.get(row, BuildsFields.NORMAL_TALENT)
    skill = sheet.get(row, BuildsFields.SKILL_TALENT)
    burst = sheet.get(row, BuildsFields.BURST_TALENT)

    guard.append_message(f'C{constellation} {character.name}: {normal} {skill} {burst}')

    plus = 0
    for talent in [normal, skill, burst]:
        if "+" in talent:
            plus += 1
            index = talent.index("+")
            guard.eq(talent[index:], "+3")
            talent = talent[:index]
            guard.eq(talent, talent.strip())
        guard.range(int(talent), 1, 10)

    guard.range(plus, 0, 2)
    if constellation < 3:
        guard.eq(plus, 0, "Invalid constellation")
    elif constellation < 5:
        guard.sniff(plus == 1, "Missing C3 talent boost")
    else:
        guard.sniff(plus == 2, "Missing C5 talent boost")


def get_rarity(rawrity: str) -> int:
    starless = rawrity.strip("★☆")
    guard.greater(len(starless), len(rawrity), f'{rawrity} -> {starless}')
    return int(starless)


class Weapon:
    def __init__(self, sheet: Sheet, row: List[str], character: CharacterRow):
        self.name = sheet.get(row, BuildsFields.WEAPON)
        self.type = character.weapon
        self.stat = sheet.get(row, BuildsFields.WEAPON_STAT)
        self.method = sheet.get(row, BuildsFields.WEAPON_METHOD)
        self.rarity: int = get_rarity(sheet.get(row, BuildsFields.WEAPON_RARITY))

    @message_guardian(guard)
    def compare(self, other: Self):
        guard.append_message(f'{self.name} / {other.name}')
        if self.name == "TODO":
            return

        guard.eq(self.name, other.name)
        guard.eq(self.type, other.type)
        guard.eq(self.stat, other.stat)
        guard.eq(self.method, other.method)
        guard.eq(self.rarity, other.rarity, "Rarity")


@message_guardian(guard)
def validate_weapon(sheet: Sheet, row: List[str], character: CharacterRow, weapon_map: Dict[str, Weapon]):
    weapon = Weapon(sheet, row, character)
    guard.append_message(f'{character.name} {weapon.name}')

    level = int(sheet.get(row, BuildsFields.WEAPON_LEVEL))
    rank = int(sheet.get(row, BuildsFields.WEAPON_RANK))
    guard.range(level, 1, 90, "Level")
    guard.range(rank, 1, 5, "Rank")

    guard.range(weapon.rarity, 1, 5, "Rarity")
    guard.uneq(weapon.rarity, 2, "Rarity")
    if weapon.rarity == 1:
        with message_guardian(guard, "1★ Requirements"):
            guard.eq(weapon.method, WeaponMethod.STANDARD, "Method")
            guard.eq(level, 1, "Level")
            guard.eq(rank, 1, "Rank")
    else:
        guard.inside(weapon.method, WeaponMethod)
        if weapon.method == WeaponMethod.SIGNATURE:
            guard.eq(weapon.rarity, 5, "Signature Rarity")
        if weapon.method in [
            WeaponMethod.LIMITED_BANNER, WeaponMethod.BATTLE_PASS, WeaponMethod.FISH,
            WeaponMethod.EVENT, WeaponMethod.FORGE
        ]:
            guard.eq(weapon.rarity, 4, "4★ Method")
        if weapon.method == WeaponMethod.BATTLE_PASS:
            guard.eq(weapon.stat, "CRIT Rate", f'BP Stat')
        if weapon.method in [WeaponMethod.FISH, WeaponMethod.EVENT]:
            guard.eq(rank, 5, f'{weapon.method} Rank')

    if weapon.name in weapon_map:
        existing = weapon_map.get(weapon.name)
        existing.compare(weapon)
    else:
        weapon_map[weapon.name] = weapon


class CharacterBuild:
    def __init__(self, sheet: Sheet, row: List[str], character: CharacterRow):
        self.character = character
        self.level = sheet.get(row, BuildsFields.CHAR_LEVEL)
        self.normal = sheet.get(row, BuildsFields.NORMAL_TALENT)
        self.skill = sheet.get(row, BuildsFields.SKILL_TALENT)
        self.burst = sheet.get(row, BuildsFields.BURST_TALENT)
        self.weapon = Weapon(sheet, row, character)


def validate_builds(characters: CharacterSheet):
    weapon_map: Dict[str, Weapon] = {}
    for tab in BUILD_TABS:
        sheet = get_sheet(tab)
        guard.append_message(tab.value)

        # Sort columns have a unique value for every index
        check_sort = sheet.has_field(BuildsFields.CHAR_SORT)
        sort_map: Dict[BuildsFields, List[bool]] = {}
        if check_sort:
            for sort_field in BUILD_SORT_FIELDS:
                sort_map[sort_field] = [False] * len(sheet.rows)

        for row in sheet.rows:
            name = sheet.get(row, BuildsFields.NAME)

            if check_sort:
                for sort_field in BUILD_SORT_FIELDS:
                    with message_guardian(guard, f'{name or "--"}, {sort_field}'):
                        sort_val = int(sheet.get(row, sort_field)) - 1
                        guard.info_if(sort_map[sort_field][sort_val], f'duplicate index {sort_val + 1}')
                        sort_map[sort_field][sort_val] = True
                if name == "":
                    continue

            character = characters.get(name)
            with message_guardian(guard, name):
                guard.range(int(sheet.get(row, BuildsFields.CHAR_LEVEL)), 20, 90, "Level")
                validate_talents(sheet, row, character)
                validate_weapon(sheet, row, character, weapon_map)

        if check_sort:
            for sort_field in BUILD_SORT_FIELDS:
                with message_guardian(guard, sort_field.name):
                    missing = [index + 1 for index, val in enumerate(sort_map[sort_field]) if not val]
                    guard.info.eq(missing, [], f"Missing sort values")
                    guard.info.eq(sum(sort_map[sort_field]), len(sheet.rows), f"Sort field total")

        guard.pop_message(tab.value)


@message_guardian(guard)
def validate_recipes(characters: CharacterSheet):
    unseen: Set[str] = set()
    for character in characters.rows:
        if character.name.endswith(" Traveler") or character.name == "Raiden Shogun":
            continue
        unseen.add(character.name)

    sheet: Sheet = get_sheet(Tab.RECIPES)
    for row in sheet.rows:
        value = sheet.get(row, "Character")
        if value:
            guard.inside(value, characters.character_map, "Unknown character")
            guard.inside(value, unseen, "Duplicate character")
            unseen.remove(value)

    guard.empty(unseen, "Missing character recipes")


@message_guardian(guard)
def validate_achievements():
    sheet = AchievementsSheet()

    index = 0
    for category in sheet.wonder_categories:
        guard.greater(index, category.start_index)
        guard.greater(category.start_index, category.end_index)
        index = category.end_index

    wonder_keys: Set[str] = set([category.key for category in sheet.wonder_categories])
    for category in sheet.jump_map.values():
        guard.bark.inside(category, wonder_keys, "Unknown jump category")

    total_achievements = len(sheet.map)
    total_category_achievements = sum([len(category.rows) for category in sheet.categories.values()])
    guard.bark.eq(total_achievements, total_category_achievements, "Totals")

    wonder = sheet.category(AchievementSections.WONDERS)
    total_wonder = len(wonder.rows)
    total_category_wonder = sum([len(category.rows) for category in sheet.wonder_categories])
    guard.bark.eq(total_wonder, total_category_wonder, "Wonder Totals")


def validate():
    characters = CharacterSheet()

    validate_character_data(characters)
    validate_builds(characters)
    validate_recipes(characters)

    validate_achievements()

