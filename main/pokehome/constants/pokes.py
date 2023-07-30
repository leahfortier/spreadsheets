from typing import List

TOTAL_POKEMON: int = 1010

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

INCLUDE_GENDER_FORM: List[str] = [
    "Unfezant", "Frillish", "Jellicent", "Meowstic", "Pyroar", "Indeedee", "Basculegion", "Oinkologne",
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
        "Frillish", "Jellicent",
        "Rotom", "Minior"
    ],
    [
        "Sinistea", "Polteageist", "Dudunsparce", "Maushold",
        "Tauros", "Basculin", "Toxtricity", "Gimmighoul",
        "Unfezant", "Meowstic", "Pyroar", "Indeedee", "Basculegion", "Oinkologne"
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