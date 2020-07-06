"""mahjong.testdata

Provide values for testing
"""

from collections import Counter
from itertools import islice

import tiles

WINNING_HAND_EXAMPLE1 = Counter(
    {tiles.TILE_ONE_OF_CHARACTERS: 1,
     tiles.TILE_TWO_OF_CHARACTERS: 1,
     tiles.TILE_THREE_OF_CHARACTERS: 3}) + Counter(islice(tiles.TILE_RANGE_BAMBOOS, 0, 8))

