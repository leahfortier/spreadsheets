from main.genshin.constants.io import ACHIEVEMENTS_INFILE, VERSIONS_OUTFILE
from main.genshin.constants.sheets import get_achievements_sheet, AchievementFields
from main.util.data import Sheet
from main.util.file_io import from_tsv, to_tsv


def add_version_column():
    # From Wonders of the World table
    # https://genshin-impact.fandom.com/wiki/Wonders_of_the_World#Achievement_List
    wiki = from_tsv(ACHIEVEMENTS_INFILE)
    version_map = {}
    for row in wiki:
        assert len(row) in [6, 7]
        name = row[0]
        version = row[-2]
        assert version_map.get(name, version) == version
        version_map[name] = version

    sheet: Sheet = get_achievements_sheet()

    out = []
    for row in sheet.rows:
        name = sheet.get(row, AchievementFields.NAME)
        version = version_map.get(name, "")
        print(name, version)
        out.append([version, name])

    to_tsv(VERSIONS_OUTFILE, out)


def update_wonders():
    pass
