import random
from typing import List

from genshin.constants.sheets import get_character_sheet, CHARACTER_NAME_FIELD, ABYSS_RANDOMIZE_CHARACTERS


def print_floor(floor: str, characters: List[str]) -> None:
    print(f'\n{floor}:\n\t{"\n\t".join(characters)}')


def randomize_abyss():
    sheet = get_character_sheet()
    characters = []
    for row in sheet.rows:
        name = sheet.get(row, CHARACTER_NAME_FIELD)
        if name != "":
            characters.append(name)

    total_randomize = sum(num for num in ABYSS_RANDOMIZE_CHARACTERS.values())
    sample = random.sample(characters, total_randomize)
    start = 0
    for floor, num in ABYSS_RANDOMIZE_CHARACTERS.items():
        print_floor(f'Floor {floor}', sample[start:start + num])
        start += num

    remaining = [character for character in characters if character not in sample]
    print_floor(f'Remaining', remaining)

