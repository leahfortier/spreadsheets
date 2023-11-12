from main.genshin.constants.io import RECIPES_INFILE, CHARACTERS_INFILE, RECIPES_OUTFILE
from main.util.file_io import from_tsv, from_file, to_file


def update_recipes():
    recipes = from_tsv(RECIPES_INFILE)
    character_to_recipe = {}

    for row in recipes:
        assert len(row) == 2
        recipe = row[0]
        character = row[1]
        if character:
            character_to_recipe[character] = recipe

    out = []
    characters = from_file(CHARACTERS_INFILE)
    assert len(characters) == len(character_to_recipe)
    for character in characters:
        if character in ["Raiden Shogun", "Traveler"]:
            recipe = "None"
        else:
            recipe = character_to_recipe[character]
        out.append(recipe)

    to_file(RECIPES_OUTFILE, out)
