from genshin.abyss import randomize_abyss
from genshin.achievements import AchievementsHandler
from genshin.characters import CharacterSheet
from genshin.validation import validate


def main():
    characters = CharacterSheet()
    achievements = AchievementsHandler()

    validate(characters, achievements)

    # randomize_abyss()


main()
