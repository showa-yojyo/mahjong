"""
PROTOTYPE

手牌を分類する。
"""

from collections import Counter
from enum import Enum
from itertools import chain, combinations, repeat
from random import sample
from typing import Iterable, Sequence, Tuple, Union

import tiles

# Filters
def _create_filter(tile_range):
    """A helper function."""
    return Counter(chain.from_iterable(repeat(tile_range, 4)))

FILTER_WINDS = _create_filter(tiles.TILE_RANGE_WINDS)
FILTER_DRAGONS = _create_filter(tiles.TILE_RANGE_DRAGONS)
FILTER_HONORS = FILTER_WINDS + FILTER_DRAGONS
FILTER_CHARACTERS = _create_filter(tiles.TILE_RANGE_CHARACTERS)
FILTER_CIRCLES = _create_filter(tiles.TILE_RANGE_CIRCLES)
FILTER_BAMBOOS = _create_filter(tiles.TILE_RANGE_BAMBOOS)
#FILTER_TERMINALS = _create_filter(tiles.TILE_TERMINALS)


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

    return (player_hand & FILTER_CHARACTERS,
            player_hand & FILTER_CIRCLES,
            player_hand & FILTER_BAMBOOS,
            player_hand & FILTER_WINDS,
            player_hand & FILTER_DRAGONS)


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

    ORPHAN = '孤立牌'
    SIMPLE_PAIR = '対子'
    SERIAL_PAIR = '両面搭子'
    SEPARATED_SERIAL_PAIR = '嵌張搭子'
    TERMINAL_SERIAL_PAIR = '辺張搭子'
    CHOW = '順子'
    PONG = '刻子'
    KONG = '槓子'

def _generate_all_pairs_suit():
    """TODO: optimize
    """

    for i in range(1, 10):
        yield (Counter((i, i)), TileTupleType.SIMPLE_PAIR)
        if i < 9:
            if i in (1, 8):
                yield (Counter((i, i + 1)), TileTupleType.TERMINAL_SERIAL_PAIR)
            else:
                yield (Counter((i, i + 1)), TileTupleType.SERIAL_PAIR)
        if i < 8:
            yield (Counter((i, i + 2)), TileTupleType.SEPARATED_SERIAL_PAIR)

_all_pairs_suit = tuple(_generate_all_pairs_suit())
_all_pairs_honor = tuple((Counter({i: 2}), TileTupleType.SIMPLE_PAIR)
                          for i in tiles.TILE_RANGE_HONORS)
_all_eyes = tuple(pair for pair, pair_type in _all_pairs_suit
                  if pair_type == TileTupleType.SIMPLE_PAIR)


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


def _generate_all_melds_suit():
    """Generate 111, 123, 222, 234, 333, 345, ..., 777, 789, 888, 999.
    """

    for i in range(1, 10):
        yield Counter({i: 3})
        if i + 2 <= 9:
            yield Counter([i, i + 1, i + 2])


_all_melds_suit = tuple(_generate_all_melds_suit())
_all_melds_honor = tuple(Counter({i: 3}) for i in tiles.TILE_RANGE_HONORS)


def classify_suit_tiles(tiles):
    """Classify numbered tiles

    ``tiles`` must be an ordered sequence.
    """

    assert tiles
    work_tiles = tiles[:]

    if (ntile := len(work_tiles)) == 1:
        return {TileTupleType.ORPHAN: (work_tiles[0],)}

    if ntile == 2:
        return {get_pair_type(work_tiles): work_tiles}

    # sequence of differences of tiles
    seq_diff = [tiles[i + 1] - tiles[i] for i in range(ntile - 2)]

    if ntile == 3:
        assert len(seq_diff) == 2
        if not any(seq_diff):
            # 00
            return {TileTupleType.PONG: work_tiles}
        if seq_diff.count(1) == 2:
            # 11
            return {TileTupleType.CHOW: work_tiles}

        # Classify a pair and a single tile.
        type_front = get_pair_type(work_tiles[:2])
        type_back = get_pair_type(work_tiles[1:])

        if type_front == type_back == TileTupleType.ORPHAN:
            return {TileTupleType.ORPHAN: work_tiles}

        return {
            {
                type_front: work_tiles[:2],
                TileTupleType.ORPHAN: work_tiles[-1],
            },
            {
                TileTupleType.ORPHAN: work_tiles[0],
                type_back: work_tiles[1:],
            },}


def get_pair_type(pair: Union[Sequence[int], Counter]) -> TileTupleType:
    """Identify the type of given pair.

    >>> print(get_pair_type((4, 4)).value)
    対子
    >>> print(get_pair_type((3, 4)).value)
    両面搭子
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
    if diff == 1:
        if lower == 1 or upper == 9:
            # 辺張
            return TileTupleType.TERMINAL_SERIAL_PAIR
        # 両面
        return TileTupleType.SERIAL_PAIR
    if diff == 2:
        # 嵌張
        return TileTupleType.SEPARATED_SERIAL_PAIR

    raise ValueError


def remove_melds(player_hand: Counter, all_melds: Tuple) -> Tuple[Counter]:
    """Remove some melds from player's hand.

    >>> remove_melds(Counter([3, 8, 9, 9]), _all_melds_suit)
    ()
    >>> remove_melds(Counter([3, 4, 5, 7]), _all_melds_suit)
    (Counter({3: 1, 4: 1, 5: 1}),)
    >>> remove_melds(Counter([8, 8]), _all_melds_suit)
    ()
    """

    remains = player_hand
    melds = []
    for meld in all_melds:
        if remains & meld == meld:
            remains -= meld
            melds.append(meld)

    return tuple(melds)


def remove_pairs(player_hand: Counter, all_pairs: Tuple) -> Tuple[Counter]:
    """Remove some pairs as incomplete melds from player's hand.

    >>> remove_pairs(Counter([3, 8, 9, 9]), _all_pairs_suit)
    (Counter({8: 1, 9: 1}),)

    >>> remove_pairs(Counter([7]), _all_pairs_suit)
    ()

    >>> remove_pairs(Counter([8, 8]), _all_pairs_suit)
    (Counter({8: 2}),)
    """

    remains = player_hand
    pairs = []
    for pair, _ in all_pairs:
        if remains & pair == pair:
            remains -= pair
            pairs.append(pair)

    return tuple(pairs)


def count_shanten_std(player_hand: Union[Counter, Iterable]) -> int:
    """Count the shanten number of player's hand to 4-melds-1-pair form.

    >>> count_shanten_std(tiles.tiles('3899m3457p88s南白発'))
    4
    >>> count_shanten_std(tiles.tiles('3899m3457p88s南発発'))
    3
    >>> count_shanten_std(tiles.tiles('389m3457p888s南発発'))
    2
    >>> count_shanten_std(tiles.tiles('89m23457p888s南発発'))
    1
    >>> count_shanten_std(tiles.tiles('88m23457p888s南発発'))
    1

    >>> count_shanten_std(tiles.tiles('1112345678999s'))
    0
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    part_m = player_hand & FILTER_CHARACTERS
    part_p = player_hand & FILTER_CIRCLES
    part_s = player_hand & FILTER_BAMBOOS
    part_m, part_p, part_s = (tiles.convert_suit_to_number(suit_part)
               for suit_part in (part_m, part_p, part_s))

    melds_m, melds_p, melds_s = (
        remove_melds(suit_part, _all_melds_suit) for suit_part in (part_m, part_p, part_s))
    pairs_m, pairs_p, pairs_s = (
        remove_pairs(suit_part, _all_pairs_suit) for suit_part in (part_m, part_p, part_s))

    hand_h = player_hand & FILTER_HONORS
    melds_h = remove_melds(hand_h, _all_melds_honor)
    pairs_h = remove_pairs(hand_h, _all_pairs_honor)

    num_shanten = 8
    num_shanten -= sum(len(melds) for melds in (
        melds_m, melds_p, melds_s, melds_h)) * 2
    num_shanten -= sum(len(pairs) for pairs in (
        pairs_m, pairs_p, pairs_s, pairs_h))

    return num_shanten


def construct_tempai_4():
    """Return all tempai of four tiles of the same suit."""

    for i in range(1, 10):
        yield from (Counter({i: 3, j: 1}) for j in range(1, 10) if j != i)
    for chow in _all_chows:
        yield from (chow + Counter({j: 1}) for j in range(1, 10))

#for tempai in construct_tempai_4():
#    print(tuple(tempai.elements()))


class WaitingInfo:
    def __init__(self):
        self.melds = []
        self.eyes = None
        self.waiting_tiles = []
        self.remain_tiles = None

    def __str__(self):
        return f'{self.eyes} {self.melds} {self.remain_tiles} {self.waiting_tiles}'

    def set_eyes(self, tile):
        self.eyes = [tile]*2

    def set_single_wait(self, tile):
        self.eyes = [tile]

    @property
    def shanten(self):
        """Return the shanten number"""
        return len(self.waiting_tiles)


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

# Features for seven pairs

def resolve_seven_pairs(player_hand):
    """Resolve all the waiting tiles as Seven Pairs.

    Note that Seven Pairs must be of seven different pairs. Two identical pairs
    are not allowed.

    >>> resolve_seven_pairs(Counter('AABBCCDDEEFFG'))
    (0, ('G',))
    >>> resolve_seven_pairs(Counter('AABBCCDDEEFGH'))
    (1, ('F', 'G', 'H'))

    A hand with four different pairs is 2-shanten of Seven Pairs:

    >>> resolve_seven_pairs(Counter('AAABBBCCCDDEF'))
    (2, ('E', 'F'))
    >>> resolve_seven_pairs(Counter('AABBCCDDEFGHI'))
    (2, ('E', 'F', 'G', 'H', 'I'))

    >>> resolve_seven_pairs(Counter('AABBCCCCDEFGH'))
    (3, ('D', 'E', 'F', 'G', 'H'))
    >>> shanten, tiles = resolve_seven_pairs(Counter('ABCDEFabcdef0'))
    >>> shanten, len(tiles)
    (6, 13)
    """

    assert isinstance(player_hand, Counter)

    npair = sum(1 for v in player_hand.values() if v >= 2)
    waiting_tiles = tuple(
        tile for tile in player_hand if player_hand[tile] < 2)

    return 6 - npair, waiting_tiles


# Features for Thirteen Orphans

_thirteen_orphans = Counter(
    chain(tiles.TILE_RANGE_HONORS, tiles.TILE_TERMINALS))

_thirteen_orphans_value_filter = Counter(
    {tile: 4 for tile in _thirteen_orphans})

def resolve_thirteen_orphans(player_hand):
    """Resolve all the waiting tiles as Thirteen Orphans.

    >>> hand = _thirteen_orphans
    >>> shanten, waiting_tiles = resolve_thirteen_orphans(hand)
    >>> shanten
    0
    >>> all(tiles.is_honor(t) or tiles.is_terminal(t) for t in waiting_tiles)
    True
    >>> len(waiting_tiles)
    13

    >>> hand = _thirteen_orphans.copy()
    >>> hand.subtract(tiles.TILE_RANGE_WINDS)
    >>> hand.update((tiles.TILE_ONE_OF_BAMBOOS,))
    >>> shanten, waiting_tiles = resolve_thirteen_orphans(hand)
    >>> shanten
    3
    >>> all(lhs == rhs for lhs, rhs in zip(
    ...     waiting_tiles, tuple(tiles.TILE_RANGE_WINDS)))
    True
    """

    assert isinstance(player_hand, Counter)

    terms_or_honors = _thirteen_orphans_value_filter & player_hand
    waiting_tiles = _thirteen_orphans - terms_or_honors
    if any(dup > 1 for dup in terms_or_honors.values()):
        # Thirteen Orphans of a single wait
        return (len(waiting_tiles) - 1, tuple(waiting_tiles.elements()))

    # Thirteen Orphans of the 13 wait
    return (len(waiting_tiles), tuple(terms_or_honors))


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

    possible_melds = tuple(meld for meld in _all_melds_suit if player_hand & meld == meld)
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
