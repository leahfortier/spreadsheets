from typing import List

import requests
from lxml import html

from pokopia.constants.io import FAVES_INFILE, SEREBII_FAVES_FILE
from util.file_io import from_tsv, to_tsv
from util.warn import GuardDog, WarnLevel

guard = GuardDog(level=WarnLevel.ASSERT)

faves = from_tsv(FAVES_INFILE)


out_rows: List[List[str]] = []
for row in faves:
    guard.eq(len(row), 2)
    fave_name = row[0].strip()
    guard.eq(row[1], "TBD")

    lookup_name = fave_name.lower().replace(" ", "")

    page = requests.get('https://www.serebii.net/pokemonpokopia/favorites/' + lookup_name + '.shtml')
    tree = html.fromstring(page.text)
    table_names = tree.xpath('/html/body/div[1]/div[2]/main/table[2]/tr/td[2]')[1:]

    item_ids = [cell.text_content() for cell in table_names]
    out_rows.append([fave_name] + item_ids)

to_tsv(SEREBII_FAVES_FILE, out_rows)
