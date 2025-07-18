from typing import Set, List, Dict, Self

from genshin.characters import CharacterSheet, CharacterRow
from genshin.constants.sheets import get_sheet, Tab, BuildsFields, BUILD_TABS, WeaponMethod, BUILD_SORT_FIELDS
from util.data import Sheet


def get_values(tab_name: Tab, field_name: str) -> Set[str]:
    values = set()
    sheet: Sheet = get_sheet(tab_name)
    for row in sheet.rows:
        values.add(sheet.get(row, field_name))
    return values


def validate_character_data(characters: CharacterSheet):
    trounces = get_values(Tab.TROUNCES, "Drop")
    boss_drops = get_values(Tab.BOSS_DROPS, "Material")
    enemy_drops = get_values(Tab.ENEMY_DROPS, "Material")
    specialties = get_values(Tab.LOCALS, "Specialty")
    recipes = get_values(Tab.RECIPES, "Recipe")
    recipes.add("None")

    for character in characters.rows:
        if character.name == "Traveler":
            continue

        assert character.trounce in trounces, character.name + " " + character.trounce
        assert character.boss_mat in boss_drops, character.name + " " + character.boss_mat
        assert character.enemy_mat in enemy_drops, character.name + " " + character.enemy_mat
        assert character.local in specialties, character.name + " " + character.local
        assert character.recipe in recipes, character.name + " " + character.recipe


def validate_talents(sheet: Sheet, row: List[str], character: CharacterRow):
    constellation = int(sheet.get(row, BuildsFields.CONSTELLATION))
    normal = sheet.get(row, BuildsFields.NORMAL_TALENT)
    skill = sheet.get(row, BuildsFields.SKILL_TALENT)
    burst = sheet.get(row, BuildsFields.BURST_TALENT)

    plus = 0
    for talent in [normal, skill, burst]:
        if "+" in talent:
            plus += 1
            index = talent.index("+")
            assert talent[index:] == "+3"
            talent = talent[:index]
            assert talent == talent.strip(), character.name
        assert 1 <= int(talent) <= 10

    assert 0 <= plus <= 2
    if constellation < 3:
        assert plus == 0, character.name
    elif constellation < 5:
        assert plus == 1, character.name
    else:
        assert plus == 2, character.name


def get_rarity(rawrity: str) -> int:
    starless = rawrity.strip("★☆")
    assert len(starless) < len(rawrity), rawrity + " -> " + starless
    return int(starless)


class Weapon:
    def __init__(self, sheet: Sheet, row: List[str], character: CharacterRow):
        self.name = sheet.get(row, BuildsFields.WEAPON)
        self.type = character.weapon
        self.stat = sheet.get(row, BuildsFields.WEAPON_STAT)
        self.method = sheet.get(row, BuildsFields.WEAPON_METHOD)
        self.rarity: int = get_rarity(sheet.get(row, BuildsFields.WEAPON_RARITY))

    def compare(self, other: Self):
        if self.name == "TODO":
            return
        assert self.name == other.name, self.name
        assert self.type == other.type, self.name
        assert self.stat == other.stat or other.stat == "", self.name
        assert self.method == other.method or other.stat == "", self.name
        assert self.rarity == other.rarity, self.name


def validate_weapon(sheet: Sheet, row: List[str], character: CharacterRow, weapon_map: Dict[str, Weapon]):
    weapon = Weapon(sheet, row, character)

    level = int(sheet.get(row, BuildsFields.WEAPON_LEVEL))
    rank = int(sheet.get(row, BuildsFields.WEAPON_RANK))
    assert 1 <= level <= 90
    assert 1 <= rank <= 5

    assert 1 <= weapon.rarity <= 5 and weapon.rarity != 2
    if weapon.rarity == 1:
        assert weapon.method in [WeaponMethod.STANDARD, ""]
        assert level == 1
        assert rank == 1
    else:
        assert weapon.method in WeaponMethod, character.name
        if weapon.method == WeaponMethod.SIGNATURE:
            assert weapon.rarity == 5, character.name
        if weapon.method in [
            WeaponMethod.LIMITED_BANNER, WeaponMethod.BATTLE_PASS, WeaponMethod.FISH,
            WeaponMethod.EVENT, WeaponMethod.FORGE
        ]:
            assert weapon.rarity == 4, character.name
        if weapon.method == WeaponMethod.BATTLE_PASS:
            assert weapon.stat == "CRIT Rate"
        if weapon.method in [WeaponMethod.FISH, WeaponMethod.EVENT]:
            assert rank == 5

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
                    sort_val = int(sheet.get(row, sort_field)) - 1
                    assert not sort_map[sort_field][sort_val], f'{sort_field} {name}'
                    sort_map[sort_field][sort_val] = True
                if name == "":
                    continue

            character = characters.get(name)
            assert 20 <= int(sheet.get(row, BuildsFields.CHAR_LEVEL)) <= 90, name
            validate_talents(sheet, row, character)
            validate_weapon(sheet, row, character, weapon_map)

        if check_sort:
            for sort_field in BUILD_SORT_FIELDS:
                assert sum(sort_map[sort_field]) == len(sheet.rows)


def validate():
    characters = CharacterSheet()

    validate_character_data(characters)
    validate_builds(characters)

