from typing import List, Dict

TOTAL_POKEMON: int = 1025

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
    "Pikachu": ["Cosplay Pikachu", "Pikachu in a cap"],
    "Darmanitan": ["Zen Mode"],
    "Kyurem": ["White Kyurem", "Black Kyurem"],
    "Greninja": ["Battle Bond", "Ash-Greninja"],
    "Floette": ["Eternal Flower"],
    "Zygarde": ["Complete"],
    "Necrozma": ["Ultra Necrozma"],
    "Calyrex": ["Ice Rider", "Shadow Rider"],

    # This should eventually be removed
    "Ursaluna": ["Bloodmoon"],
}