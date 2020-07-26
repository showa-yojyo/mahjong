"""
mahjong.walls
"""

from itertools import (chain, repeat)
from random import shuffle
import tiles

# TODO: Take a tile from the dead wall after a kong
# TODO: Shift haitei, the last tile of live wall
class TileWallAgent:
    """The wall

    >>> walls = TileWallAgent()
    >>> player_hands = walls.build()
    >>> len(player_hands)
    4
    >>> all(len(player_hand) == 13 for player_hand in player_hands)
    True
    >>> len(walls.live_wall)
    70
    >>> len(walls.dead_wall)
    14
    """

    DEAD_WALL_SIZE = 14

    def __init__(self):
        self.num_revealed_tiles = 0
        self.dead_wall = None
        self.live_wall = None


    def build(self):
        """Shuffle tiles, build the wall, reveal the first dora indicator
        and let the players take 13 tiles.
        """

        self._shuffle_tiles()
        self._reveal_dora()
        return self._do_initial_deal()


    def _shuffle_tiles(self):
        """Shuffle all tiles and build the wall.
        """

        all_tiles = list(chain.from_iterable(repeat(tiles.TILE_RANGE, 4)))
        shuffle(all_tiles)
        self.dead_wall = all_tiles[:self.DEAD_WALL_SIZE]
        self.live_wall = all_tiles[self.DEAD_WALL_SIZE:]


    def _reveal_dora(self):
        """Turn the first dora indicator over.
        """

        self.num_revealed_tiles = 1


    def reveal_kong_dora(self):
        """Turn a kong dora indicator over.
        """

        if self.num_revealed_tiles == 5:
            raise ValueError('Too many Kong-dora indicators')
        self.num_revealed_tiles += 1


    def _do_initial_deal(self, num_player=4):
        """Let the players take 13 tiles"""

        num_tiles_took = 4
        curpos = -1

        player_hands = [list() for _ in range(num_player)]

        took_part = slice(curpos, curpos - num_tiles_took, -1)
        for _ in range(3):
            for player_hand in player_hands:
                player_hand.extend(self.live_wall[took_part])
                del self.live_wall[took_part]

        num_tiles_took = 1
        for player_hand in player_hands:
            player_hand.append(self.live_wall[-1])
            self.live_wall.pop()

        return player_hands
