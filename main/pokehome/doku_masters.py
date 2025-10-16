from typing import List

from pokehome.constants.io import DOKU_SHINIES_OUTFILE
from pokehome.constants.sheets import get_shiny_tracker_sheet
from pokehome.db import Database
from util.data import Sheet
from util.file_io import to_file
from util.general import warn


def get_form(db: Database, full_name: str, form_name: str, poke_name: str):
    if form_name == "Gmax":
        form_name = "Gigantamax"
    if poke_name == "Paldean Tauros":
        full_name = f"Paldean Tauros ({form_name})"
        poke_name = "Tauros"

    if poke_name in db.species_map:
        all_forms = db.species_map[poke_name]
        for form_id in all_forms:
            form = db.get(form_id)
            if (form.name == full_name or form.digimon_form == form_name
                    or form.form == form_name or form.gender_form == form_name
                    or any(form.form.removesuffix(suffix).strip() == form_name for suffix in [" Style", " Flower", " Mane"])):
                return form_id

        warn("No form found: " + full_name)
        return f"Broken {poke_name} Form"
    return None


def get_poke_id(db: Database, shiny: str) -> str:
    # Shield form is base
    if shiny == "Shield Aegislash":
        shiny = "Aegislash"

    # Poke name is full string -- base form
    if shiny in db.species_map:
        return db.species_map[shiny][0]

    # Try removing the first word as a form
    split = shiny.split(" ", 1)
    form_id = get_form(db, shiny, split[0], split[-1])
    if form_id:
        return form_id

    # Try the first word as the poke
    form_id = get_form(db, shiny, split[-1], split[0])
    if form_id:
        return form_id

    # Try removing the last word as a form
    split = shiny.rsplit(" ", 1)
    form_id = get_form(db, shiny, split[0], split[-1])
    if form_id:
        return form_id

    # Try the last word as the poke
    form_id = get_form(db, shiny, split[-1], split[0])
    if form_id:
        return form_id

    warn("No poke found: " + shiny)
    return "Unknown"


class Shiny:
    def __init__(self, db: Database, date: str, shiny: str):
        self.date = date
        self.shiny = shiny
        self.poke_id = get_poke_id(db, shiny)

    def __str__(self):
        return f'{self.date} {self.shiny} {self.poke_id}'


class Player:
    def __init__(self, db: Database, player_name: str):
        self.db = db

        self.name = player_name
        self.shinies: List[Shiny] = []

    def add_shiny(self, date: str, shiny: str):
        self.shinies.append(Shiny(self.db, date, shiny))

    def number_order(self):
        return sorted(self.shinies, key=lambda shiny: shiny.poke_id)


def get_shinies(values: str) -> List[str]:
    split = [shiny.strip() for shiny in values.split(",") if shiny]

    return split


class DokuMasters:
    def __init__(self, db: Database):
        self.sheet: Sheet = get_shiny_tracker_sheet()
        self.players = []
        for field_name in self.sheet.schema_row:
            if field_name and field_name not in ["Date", "Notes"]:
                self.players.append(Player(db, field_name))

        for index, row in enumerate(self.sheet.rows):
            date = self.sheet.get(row, "Date")
            if not date:
                continue
            if date == "BONUS":
                date = self.sheet.get(self.sheet.rows[index - 1], "Date") + " BONUS"
            for player in self.players:
                shinies = get_shinies(self.sheet.get(row, player.name))
                for shiny in shinies:
                    player.add_shiny(date, shiny)

    def write(self):
        out_rows = []
        for player in self.players:
            out_rows.append(f'{player.name} ({len(player.shinies)}):')
            for shiny in player.number_order():
                out_rows.append(f'\t{shiny}')

        to_file(DOKU_SHINIES_OUTFILE, out_rows, show_diff=False)
