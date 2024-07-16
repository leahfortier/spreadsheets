from typing import List, Dict

from pokehome.constants.sheets import EMPTY_FIELD

TOTAL_POKEMON: int = 1025
CURRENT_GENERATION = 9

BOX_ROWS: int = 5
BOX_COLS: int = 6
POKES_PER_BOX: int = BOX_ROWS * BOX_COLS
BOXES_PER_PAGE: int = 30

NATIONAL_DEX_START_PAGE: int = 6

REGIONS: List[str] = [
    "Kanto",
    "Johto",
    "Hoenn",
    "Sinnoh",
    "Unova",
    "Kalos",
    "Alola",
    "Galar",
    "Hisui",
    "Paldea"
]

REGIONALS: List[str] = [
    "Alolan",
    "Galarian",
    "Hisuian",
    "Paldean"
]

DIGIMON: List[str] = [
    "Mega",
    "Primal",
    "Gigantamax",
    "Cowboy",  # Caterpie
    "Ultra",  # Necrozma
]

EXCLUDE_BASE_FORM: List[str] = [
    "Sinistea", "Polteageist", "Dudunsparce", "Tornadus", "Thundurus", "Landorus", "Enamorus",
]

INCLUDE_UNBREEDABLE_POKEBALLS: List[str] = [
    "Pichu", "Cleffa", "Igglybuff", "Togepi",
    "Tyrogue", "Smoochum", "Elekid", "Magby",
    "Azurill", "Wynaut", "Budew", "Chingling",
    "Bonsly", "Mime Jr.", "Happiny", "Munchlax",
    "Riolu", "Mantyke", "Toxel"
]

INCLUDE_GENDER_FORM: List[str] = [
    "Hippopotas", "Hippowdon",
    "Unfezant",
    "Frillish", "Jellicent",
    "Meowstic",
    "Pyroar",
    "Indeedee",
    "Basculegion",
    "Oinkologne",
    "Alcremie",  # Special case where gender form is used for non-gender things
]

FORM_BOXES: List[List[str]] = [
    [
        "Flabébé", "Floette", "Florges"
    ],
    [
        "Deerling", "Sawsbuck",
        "Pumpkaboo", "Gourgeist",
        "Tatsugiri"
    ],
    [
        "Oricorio", "Lycanroc", "Squawkabilly",
        "Burmy", "Wormadam"
    ],
    [
        "Shellos", "Gastrodon",
        "Rotom", "Minior"
    ],
    [
        "Hippopotas", "Hippowdon",
        "Frillish", "Jellicent",
        "Unfezant", "Meowstic", "Pyroar", "Indeedee", "Basculegion", "Oinkologne"
    ],
    [
        "Sinistea", "Polteageist", "Dudunsparce", "Maushold",
        "Tauros", "Basculin", "Toxtricity", "Gimmighoul",
    ],
    [
        "Pikachu", "Furfrou"
    ],
    [
        "Deoxys", "Shaymin", "Palkia", "Dialga", "Giratina",
        "Tornadus", "Thundurus", "Landorus", "Enamorus",
        "Zygarde", "Hoopa", "Zarude", "Urshifu",
    ],
]

BALL_NOTES: Dict[str, str] = {
    "Dream": " - 6IV Nidoran♂, Mudkip",
    "Premier": " - 6IV Beldum, Impidimp, Rellor",
    "Beast": " - 6IV Tyrogue, Ralts, Dreepy",
    "Safari": " - 6IV Teddiursa",
    "Fast": " - 6IV Torchic",
    "Dusk": " - 6IV Jangmo-o",
    "Moon": " - 2 Rockruff (Own Tempo, Steadfast)",
}

NON_HOME_FORMS: Dict[str, List[str]] = {
    "Darmanitan": ["Zen Mode"],
    "Kyurem": ["White Kyurem", "Black Kyurem"],
    "Greninja": ["Ash"],
    "Floette": ["Eternal Flower"],
    "Zygarde": ["Complete"],
    "Minior": ["Meteor"],
    "Calyrex": ["Ice Rider", "Shadow Rider"],
}

NON_DOKU_FORMS: List[str] = [
    "Pikachu", "Unown", "Burmy",
    "Shellos", "Gastrodon", "Arceus",
    "Deerling", "Sawsbuck", "Vivillon",
    "Flabébé", "Floette", "Florges",
    "Furfrou", "Sinistea", "Polteageist",
    "Alcremie"
]

DOKU_INCLUDE_GENDER_FORM: List[str] = [
    "Meowstic",
    "Indeedee",
    "Basculegion",
    "Oinkologne",
]

ALL_TYPES: List[str] = [
    "Fire", "Water", "Grass",
    "Electric", "Ice", "Fighting",
    "Poison", "Ground", "Flying",
    "Psychic", "Bug", "Rock",
    "Ghost", "Dark", "Dragon",
    "Steel", "Fairy", "Normal",
]

# Megas are not included in the Types list so handling manually for those that differs
DIGIMON_TYPES: Dict[str, List[str]] = {
    "Mega Charizard X": ["Fire", "Dragon"],
    "Mega Pinsir": ["Bug", "Flying"],
    "Mega Gyarados": ["Water", "Dark"],
    "Mega Mewtwo X": ["Psychic", "Fighting"],
    "Mega Ampharos": ["Electric", "Dragon"],
    "Mega Aggron": ["Steel", EMPTY_FIELD],
    "Mega Altaria": ["Dragon", "Fairy"],
    "Primal Groudon": ["Ground", "Fire"],
    "Mega Lopunny": ["Normal", "Fighting"],
    "Mega Audino": ["Normal", "Fairy"],
    "Ultra Necrozma": ["Psychic", "Dragon"],
}
