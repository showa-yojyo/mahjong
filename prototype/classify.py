"""
PROTOTYPE

手牌を分類する。
"""

from collections import Counter
from enum import Enum
from itertools import chain, combinations
from random import sample
from typing import Sequence, Tuple, Union

import tiles


def classify(player_hand: Counter) -> Tuple[Counter]:
    """Classify tiles by types

    >>> m, p, s, w, d = classify(Counter(tiles.tiles('1112345678999m')))
    >>> all(tiles.is_character(t) for t in m)
    True
    >>> all(tiles.is_circles(t) for t in p)
    True
    >>> all(tiles.is_bamboo(t) for t in s)
    True
    >>> all(tiles.is_wind(t) for t in w)
    True
    >>> all(tiles.is_dragon(t) for t in d)
    True
    """

    return (player_hand & tiles.FILTER_CHARACTERS,
            player_hand & tiles.FILTER_CIRCLES,
            player_hand & tiles.FILTER_BAMBOOS,
            player_hand & tiles.FILTER_WINDS,
            player_hand & tiles.FILTER_DRAGONS)


# the 36 tiles of the same suit
_tiles36 = tuple(chain.from_iterable(range(1, 10) for _ in range(4)))


def random_flush_hand(num=13):
    """Return a list of random numbers.

    >>> num = 13
    >>> numbers = random_flush_hand(num)
    >>> len(numbers) == num
    True
    >>> all(isinstance(i, int) for i in numbers)
    True
    >>> all(1 <= i <= 9 for i in numbers)
    True
    >>> any(numbers.count(i) > 5 for i in range(1, 10))
    False
    """

    return sample(_tiles36, num)


class TileTupleType(Enum):
    """Types of a tuple of tiles"""

    NONE = '無関係'
    ORPHAN = '孤立牌'
    SIMPLE_PAIR = '対子'
    SERIAL_PAIR = '両面搭子'
    SEPARATED_SERIAL_PAIR = '嵌張搭子'
    TERMINAL_SERIAL_PAIR = '辺張搭子'
    CHOW = '順子'
    PONG = '刻子'
    KONG = '槓子'

class Pong:
    """A Pong."""

    __slots__ = ('tile',)

    def __init__(self, tile):
        self.tile = tile

    def __repr__(self):
        return f'Pong({self.tile})'

    def as_counter(self):
        """
        >>> pong1 = Pong(1)
        >>> pong1.as_counter()
        Counter({1: 3})
        """
        return _all_pongs[self.tile - 1]


class Chow:
    """A Chow."""

    __slots__ = ('first',)

    def __init__(self, first):
        self.first = first

    def __repr__(self):
        return f'Chow({self.first}{self.first + 1}{self.first + 2})'

    def as_counter(self):
        """
        >>> chow123 = Chow(1)
        >>> chow123.as_counter()
        Counter({1: 1, 2: 1, 3: 1})
        """
        return _all_chows[self.first - 1]


_all_pongs = tuple(Counter((i, i, i,)) for i in range(1, 10))
_all_chows = tuple(Counter((i, i + 1, i + 2,)) for i in range(1, 8))
_all_chows_d = tuple(Counter({i: 2, i + 1: 2, i + 2: 2}) for i in range(1, 8))
_all_chows_t = tuple(Counter({i: 3, i + 1: 3, i + 2: 3}) for i in range(1, 8))
_all_chows_q = tuple(Counter({i: 4, i + 1: 4, i + 2: 4}) for i in range(1, 8))


def get_pair_type(pair: Union[Sequence[int], Counter]) -> TileTupleType:
    """Identify the type of given pair.

    One of the pair must be the same Suit or Honor as the other.

    >>> print(get_pair_type((4, 4)).value)
    対子
    >>> print(get_pair_type(tiles.tiles('東東')).value)
    対子

    >>> print(get_pair_type((3, 4)).value)
    両面搭子
    >>> print(get_pair_type(tiles.tiles('東南')).value)
    無関係

    >>> print(get_pair_type((7, 9)).value)
    嵌張搭子
    >>> print(get_pair_type((1, 2)).value)
    辺張搭子
    >>> print(get_pair_type(Counter([8, 9])).value)
    辺張搭子
    """

    if isinstance(pair, (list, tuple,)):
        assert len(pair) == 2
        lower, upper = pair
    elif isinstance(pair, Counter):
        assert sum(pair.values()) == 2
        lower, upper = min(pair), max(pair)

    diff = upper - lower
    if diff == 0:
        # 対子
        return TileTupleType.SIMPLE_PAIR

    if tiles.is_honor(lower) or tiles.is_honor(upper):
        return TileTupleType.NONE


    if diff == 1:
        if lower == 1 or upper == 9:
            # 辺張
            return TileTupleType.TERMINAL_SERIAL_PAIR
        # 両面
        return TileTupleType.SERIAL_PAIR
    if diff == 2:
        # 嵌張
        return TileTupleType.SEPARATED_SERIAL_PAIR

    return TileTupleType.NONE


def get_meld_type(meld: Union[Sequence[int], Counter]) -> TileTupleType:
    """Identify the type of a meld.

    One of the pair must be the same Suit or Honor as the other.

    >>> print(get_meld_type((1, 1, 1)).value)
    刻子
    >>> print(get_meld_type(tiles.MELDS_NUMBER[-1]).value)
    刻子
    >>> print(get_meld_type(tiles.MELDS_HONOR[-1]).value)
    刻子
    >>> print(get_meld_type((1, 2, 3)).value)
    順子
    >>> print(get_meld_type(tiles.MELDS_NUMBER[1]).value)
    順子
    >>> print(get_meld_type((1, 4, 9)).value)
    無関係
    """

    if isinstance(meld, Counter):
        meld = sorted(meld.elements())

    if any(tiles.is_honor(i) for i in meld):
        if any(tiles.is_suit(i) for i in meld):
            return TileTupleType.NONE

    if all(meld[0] == i for i in meld):
        return TileTupleType.PONG

    if meld[2] - meld[1] == meld[1] - meld[0] == 1:
        return TileTupleType.CHOW

    return TileTupleType.NONE


def get_possible_pongs(tile_counter):
    """Return all the possible pongs in tiles

    >>> get_possible_pongs(Counter([3,3,3,3,4,4,4,4,5,5,5,5,6]))
    [Pong(3), Pong(4), Pong(5)]
    """

    return [Pong(*p.keys()) for p in _all_pongs if tile_counter & p == p]


def get_possible_chows(tile_counter):
    """Return all the possible chows in tiles with multiplicity.

    >>> get_possible_chows(Counter([3,3,3,3,4,4,4,4,5,5,5,5,6]))
    [Chow(345), Chow(345), Chow(345), Chow(345), Chow(456)]
    """

    possible_chows = []
    done = set()

    multiplicity = 4
    for container in (_all_chows_q, _all_chows_t, _all_chows_d, _all_chows):
        for i, chow in enumerate(container, start=1):
            if i not in done and tile_counter & chow == chow:
                possible_chows.extend([Chow(i)] * multiplicity)
                done.add(i)
        multiplicity -= 1

    return possible_chows


def resolve_melds_single_wait(player_hand):
    """WIP"""

    possible_melds = set(combinations(chain(
        get_possible_pongs(player_hand),
        get_possible_chows(player_hand)), sum(player_hand.values()) // 3))
    for melds in possible_melds:
        counter_melds = Counter()
        for meld in melds:
            counter_melds += meld.as_counter()
        if any(v > 4 for v in counter_melds.values()):
            continue

        assert player_hand & counter_melds == counter_melds
        remains = player_hand - counter_melds
        print(remains, melds)


def resolve_melds_with_eyes(player_hand, eyes):
    """WIP"""

    possible_melds = set(combinations(chain(
        get_possible_pongs(player_hand),
        get_possible_chows(player_hand)), sum(player_hand.values()) // 3))
    for melds in possible_melds:
        counter_melds = Counter()
        for meld in melds:
            counter_melds += meld.as_counter()
        if any(v > 4 for v in counter_melds.values()):
            continue

        if player_hand & counter_melds != counter_melds:
            continue

        remains = player_hand - counter_melds
        print(eyes, remains, melds)


def resolve_melds_demo(player_hand: Counter):
    """WIP"""

    resolve_melds_single_wait(player_hand)
    for tile in player_hand:
        if player_hand[tile] >= 2:
            eyes = Counter({tile: 2})
            resolve_melds_with_eyes(player_hand - eyes, eyes)


# resolve_recursively(Counter([1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9]))
def resolve_recursively(player_hand: Counter, melds_found=None):
    """WIP

    >>> resolve_recursively(Counter([1, 3, 4, 6, 8, 9]))

    """

    if not melds_found:
        melds_found = []

    depth = len(melds_found)

    def print_melds(melds):
        for meld in melds:
            print(tuple(meld.elements()), end=' ')

    possible_melds = tuple(meld for meld in tiles.MELDS_NUMBER
                           if player_hand & meld == meld)
    if not possible_melds:
        # 雀頭探し
        print(' '*depth, end='')
        print_melds(melds_found)
        #print(tuple(player_hand.elements()), 'remains?')
        return

    for meld in possible_melds:
        melds_found.append(meld)
        resolve_recursively(player_hand - meld, melds_found)
        melds_found.pop()
