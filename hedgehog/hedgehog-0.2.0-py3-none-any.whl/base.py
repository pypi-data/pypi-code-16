# coding: utf-8


class SteamBase:
    support_games = {
        'dod': {'title': 'Day of Defeat: Source', 'id': 232290},
        'css': {'title': 'Counter-Strike: Source', 'id': 232330},
        # 'cs_go': {'title': 'Counter-Strike: Global Offensive', 'id': 740}
    }

    def get_game_id(self, game_str):
        if game_str not in self.support_games:
            raise AttributeError('Game \'%s\' not supports' % game_str)

        return self.support_games[game_str]['id']
