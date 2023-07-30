from typing import List

from main.pokehome.constants.pokes import POKES_PER_BOX, TOTAL_POKEMON, NATIONAL_DEX_START_PAGE, BOXES_PER_PAGE


class Box:
    def __init__(self, page: int, box: int, name: str, pokes: List[str]):
        self.page: str = str(page)
        self.box: str = str(box)
        self.name: str = str(name)
        self.ids = pokes

class Boxes:
    def __init__(self):
        self.boxes: List[Box] = []

    def page(self) -> int:
        return NATIONAL_DEX_START_PAGE + len(self.boxes) // BOXES_PER_PAGE

    def box(self) -> int:
        return len(self.boxes) % BOXES_PER_PAGE + 1

    def add_box(self, box_name: str, ids: List[id]) -> Box:
        self.boxes.append(Box(self.page(), self.box(), box_name, ids))
        return self.boxes[-1]

    def add_base_box(self) -> Box:
        lower: int = len(self.boxes)*POKES_PER_BOX + 1
        upper: int = min(lower + POKES_PER_BOX - 1, TOTAL_POKEMON)
        box_name = f'{lower:04d} - {upper:04d}'
        ids = [f'{num:04d}' for num in range(lower, upper + 1)]
        return self.add_box(box_name, ids)

    def dex_finished(self):
        return len(self.boxes)*POKES_PER_BOX >= TOTAL_POKEMON
