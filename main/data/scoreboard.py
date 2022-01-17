from typing import List, Dict, Iterable

from main.data.player import Player


class Scoreboard:
    def __init__(self, player_names: Iterable[str], rows: List[List[str]], start_index: int = 1):
        self.player_map: Dict[str, Player] = {}
        for player_name in player_names:
            self.player_map[player_name] = Player(player_name)

        current_mode = ''
        for row in rows:
            index = start_index
            mode = row[index]
            if mode != '':
                current_mode = mode
            chapter = row[index + 1]
            for player_name in player_names:
                index += 2
                player: Player = self.get(player_name)
                player.add_record(current_mode, chapter, row[index], row[index + 1])

    def get(self, player_name: str) -> Player:
        if player_name not in self.player_map:
            print(f'Player "{player_name}" not in map.')

        return self.player_map[player_name]

    def players(self) -> Iterable[str]:
        return self.player_map.keys()



