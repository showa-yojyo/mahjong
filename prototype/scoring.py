"""mahjong.scoring
"""

from collections import Counter

from melds import is_pair_eyes, remove_melds, remove_pairs
import tiles
from winds import Winds

class PlayerHand:
    """Player's hand."""

    def __init__(self, concealed, exposed):
        self._concealed = concealed
        self._exposed = exposed

    @property
    def is_concealed(self) -> bool:
        """Determine if all the tile is concealed."""
        return not self._exposed

    @property
    def concealed_parts(self):
        """Return concealed tiles."""
        return self._concealed

    @property
    def exposed_parts(self):
        """Return exposed melds."""
        return self._exposed


# 22m67s 5s (234s) (456m) (567p)


def _compute_minipoints_meld(tile: int, concealed: bool, value: int) -> int:
    """A helper function"""

    if not tiles.is_simple(tile):
        value <<= 1
    if concealed:
        value <<= 1

    return value


def compute_minipoints_pung(tile: int, concealed: bool) -> int:
    """Compute the value of minipoint (fu) of a Chow.

    >>> compute_minipoints_pung(tiles.tiles('2m'), False)
    2
    >>> compute_minipoints_pung(tiles.tiles('7p'), True)
    4
    >>> compute_minipoints_pung(tiles.tiles('西'), False)
    4
    >>> compute_minipoints_pung(tiles.tiles('9s'), True)
    8
    """

    return _compute_minipoints_meld(tile, concealed, 2)


def compute_minipoints_kong(tile: int, concealed: bool) -> int:
    """Compute the value of minipoint (fu) of a Kong.

    >>> compute_minipoints_kong(tiles.tiles('2m'), False)
    8
    >>> compute_minipoints_kong(tiles.tiles('7p'), True)
    16
    >>> compute_minipoints_kong(tiles.tiles('西'), False)
    16
    >>> compute_minipoints_kong(tiles.tiles('9s'), True)
    32
    """

    return _compute_minipoints_meld(tile, concealed, 8)


def compute_minipoints_eyes(
        tile: int, seat_wind: Winds, prevalent_wind: Winds) -> int:
    """Compute the value of minipoints (fu) of the Eyes.

    >>> compute_minipoints_eyes(tiles.tiles('1m'), Winds.EAST, Winds.EAST)
    0
    >>> compute_minipoints_eyes(tiles.TILE_EAST_WIND, Winds.NORTH, Winds.EAST)
    2
    >>> compute_minipoints_eyes(tiles.TILE_NORTH_WIND, Winds.NORTH, Winds.EAST)
    2
    >>> compute_minipoints_eyes(tiles.TILE_NORTH_WIND, Winds.SOUTH, Winds.EAST)
    0

    Note that Eyes are worth at most 2 minipoints. Especially double-wind is not
    applied.

    >>> compute_minipoints_eyes(tiles.TILE_EAST_WIND, Winds.EAST, Winds.EAST)
    2
    >>> compute_minipoints_eyes(tiles.TILE_SOUTH_WIND, Winds.SOUTH, Winds.SOUTH)
    2
    >>> compute_minipoints_eyes(tiles.TILE_EAST_WIND, Winds.EAST, Winds.SOUTH)
    2
    >>> compute_minipoints_eyes(tiles.TILE_EAST_WIND, Winds.SOUTH, Winds.SOUTH)
    0
    """

    if tiles.is_dragon(tile):
        return 2

    if not tiles.is_wind(tile):
        return 0

    wind_mapping = {
        tiles.TILE_EAST_WIND: Winds.EAST,
        tiles.TILE_SOUTH_WIND: Winds.SOUTH,
        tiles.TILE_WEST_WIND: Winds.WEST,
        tiles.TILE_NORTH_WIND: Winds.NORTH,}

    if wind_mapping[tile] in (seat_wind, prevalent_wind):
        return 2

    return 0


def compute_minipoints_winning(
        concealed_part: Counter, winning_tile: int) -> int:
    """Compute the value of minipoints (fu) on winning.

    Winning on an edge, closed or pair wait is worth 2 minipoints.

    >>> compute_minipoints_winning(tiles.tiles('56789p西西'), tiles.tiles('7p'))
    2
    >>> compute_minipoints_winning(tiles.tiles('56789p西西'), tiles.tiles('4p'))
    0
    >>> compute_minipoints_winning(tiles.tiles('4455677s'), tiles.tiles('6s'))
    2
    >>> compute_minipoints_winning(tiles.tiles('4455677s'), tiles.tiles('3s'))
    0
    >>> compute_minipoints_winning(tiles.tiles('1m'), tiles.tiles('1m'))
    2

    >>> compute_minipoints_winning(tiles.tiles('東東発発'), tiles.tiles('発'))
    0
    >>> compute_minipoints_winning(tiles.tiles('東東東発'), tiles.tiles('発'))
    2
    """

    # A pair wait a.k.a. single wait
    if isinstance(concealed_part, int):
        return 2

    if not isinstance(concealed_part, Counter):
        concealed_part = Counter(concealed_part)

    # A pair wait a.k.a. single wait
    if sum(concealed_part.values()) == 1:
        return 2

    tile_class = tiles.get_tile_class(winning_tile)
    if tile_class == tiles.TileClass.HONOR:
        # single wait (2) or twin Pungs (0)
        return 2 if concealed_part[winning_tile] == 1 else 0

    # Hereafter case of Suits

    hand_part = Counter({(k - tiles.TILE_ONE_OF_CHARACTERS) % 9 + 1: v
                         for k, v in concealed_part.items()
                         if tiles.get_tile_class(k) == tile_class})

    wintilenum = (winning_tile - tiles.TILE_ONE_OF_CHARACTERS) % 9 + 1
    if is_edge_wait(hand_part, wintilenum):
        return 2
    if is_closed_wait(hand_part, wintilenum):
        return 2
    if is_single_wait(hand_part, wintilenum):
        return 2

    return 0


def is_edge_wait(player_hand: Counter, winning_tile: int) -> bool:
    """Determine if an edge wait holds.

    >>> is_edge_wait(Counter([8, 9]), 7)
    True
    >>> is_edge_wait(Counter([5, 6, 7, 8, 9]), 7)
    True
    >>> is_edge_wait(Counter([7, 8, 8, 9, 9]), 7)
    True
    >>> is_edge_wait(Counter([8, 9, 9, 9]), 7)
    True
    >>> is_edge_wait(Counter([8, 8, 8, 9]), 7)
    True
    >>> is_edge_wait(Counter([8, 8, 9, 9]), 7)
    False
    >>> is_edge_wait(Counter([7, 7, 8, 8, 8, 9, 9, 9]), 7)
    True

    >>> is_edge_wait(Counter([1, 2]), 3)
    True
    >>> is_edge_wait(Counter([1, 2, 3, 4, 5]), 3)
    True
    >>> is_edge_wait(Counter([1, 1, 1, 2]), 3)
    True
    >>> is_edge_wait(Counter([1, 2, 2, 2]), 3)
    True
    >>> is_edge_wait(Counter([1, 1, 2, 2]), 3)
    False
    """

    if winning_tile == 7:
        terminal_serial_pair = Counter((8, 9))
    elif winning_tile == 3:
        terminal_serial_pair = Counter((1, 2))
    else:
        return False

    return _is_pair_wait_common(player_hand, terminal_serial_pair)


def is_closed_wait(player_hand: Counter, winning_tile: int) -> bool:
    """Test if a closed wait holds.

    >>> is_closed_wait(Counter([7, 9]), 8)
    True
    >>> is_closed_wait(Counter([7, 9, 9, 9]), 8)
    True
    >>> is_closed_wait(Counter([7, 7, 7, 9]), 8)
    True
    >>> is_closed_wait(Counter([7, 7, 9, 9]), 8)
    False

    >>> is_closed_wait(Counter([1, 3]), 2)
    True
    >>> is_closed_wait(Counter([1, 3, 3, 3]), 2)
    True
    >>> is_closed_wait(Counter([1, 1, 1, 3]), 2)
    True
    >>> is_closed_wait(Counter([1, 1, 3, 3]), 2)
    False

    >>> is_closed_wait(Counter([4, 4, 5, 5, 6, 7, 7]), 6)
    True
    """

    if winning_tile in (1, 9):
        return False

    closed_pair = Counter((winning_tile - 1, winning_tile + 1))
    meld = Counter(range(winning_tile - 1, winning_tile + 2))
    return _is_pair_wait_common(player_hand, closed_pair, meld)


def is_single_wait(player_hand: Counter, winning_tile: int) -> bool:
    """Test if a single wait holds.

    ノベタン（順子＋単騎）

    >>> is_single_wait(Counter([6, 7, 8, 9]), 6)
    True
    >>> is_single_wait(Counter([6, 7, 8, 9]), 9)
    True

    対子＋両面 or 順子＋単騎

    >>> is_single_wait(Counter([6, 6, 7, 8]), 6)
    True
    >>> is_single_wait(Counter([7, 8, 9, 9]), 9)
    True

    嵌張＋対子 or 刻子＋単騎

    >>> is_single_wait(Counter([7, 9, 9, 9]), 7)
    True
    >>> is_single_wait(Counter([7, 7, 7, 9]), 9)
    True
    """

    if winning_tile not in player_hand:
        return False

    remains = player_hand - Counter((winning_tile,))
    remove_melds(remains, tiles.MELDS_NUMBER)
    if remains:
        return False

    return True


def _is_pair_wait_common(player_hand: Counter, testing_pair: Counter, meld=None) -> bool:
    """Test if a specific pair wait holds.
    """

    if player_hand & testing_pair != testing_pair:
        return False

    remains = player_hand - testing_pair
    if meld:
        while remains & meld == meld:
            remains -= meld

    remove_melds(remains, tiles.MELDS_NUMBER)
    pairs = remove_pairs(remains, tiles.PAIRS_NUMBER)
    if remains or (len(pairs) == 1 and not is_pair_eyes(pairs[0])):
        return False

    return True


def compute_minipoints(
        self_draw_bonus: bool,
        eyes_bonus: bool,
        waiting_bonus: bool,
        concealed_melds, exposed_melds) -> int:
    """Compute minipoints from a winning hand.
    """

    if not concealed_melds and not exposed_melds:
        # Regard as Seven Pairs
        return 25

    total_minipoints = 0

    # 副底
    if not exposed_melds:
        total_minipoints += 30
    else:
        total_minipoints += 20

    # ツモ 2 符
    if self_draw_bonus:
        total_minipoints += 2

    # 雀頭 2 符
    if eyes_bonus:
        total_minipoints += 23457

    # 愚形待ち 2 符
    if waiting_bonus:
        total_minipoints += 2

    return total_minipoints
