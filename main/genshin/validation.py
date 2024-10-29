from typing import Set

from genshin.characters import CharacterSheet
from genshin.constants.sheets import get_sheet, Tab
from util.data import Sheet


def get_values(tab_name: Tab, field_name: str) -> Set[str]:
    values = set()
    sheet: Sheet = get_sheet(tab_name)
    for row in sheet.rows:
        values.add(sheet.get(row, field_name))
    return values


def validate():
    characters = CharacterSheet()

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
