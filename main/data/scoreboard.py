from typing import List, Dict, Iterable

from main.data.records import Records


class Scoreboard:
    def __init__(self, player_names: Iterable[str], rows: List[List[str]], start_index: int = 1):
        self.player_map: Dict[str, Records] = {}
        for player_name in player_names:
            self.player_map[player_name] = Records(player_name)

        current_mode = ''
        for row in rows:
            index = start_index
            mode = row[index]
            if mode != '':
                current_mode = mode
            chapter = row[index + 1]
            for player_name in player_names:
                index += 2
                records: Records = self.player_map[player_name]
                records.add_record(current_mode, chapter, row[index], row[index + 1])

    def get(self, player_name: str) -> Records:
        if player_name not in self.player_map:
            print(f'Player "{player_name}" not in map.')

        return self.player_map[player_name]

    def players(self) -> Iterable[str]:
        return self.player_map.keys()



