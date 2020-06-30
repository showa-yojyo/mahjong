"""
PROTOTYPE

手牌を分類する。
"""

from collections import Counter
from enum import Enum, auto
from itertools import chain, combinations
from random import sample

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

    ISOLATED = auto()
    SIMPLE_PAIR = auto()
    SERIAL_PAIR = auto()
    SEPARATED_SERIAL_PAIR = auto()
    TERMINAL_SERIAL_PAIR = auto()
    CHOW = auto()
    PONG = auto()
    KONG = auto()

_all_eyes = tuple(Counter((i, i,)) for i in range(1, 10))
_all_pongs = tuple(Counter((i, i, i,)) for i in range(1, 10))
_all_chows = tuple(Counter((i, i + 1, i + 2,)) for i in range(1, 8))
_all_chows_d = tuple(Counter({i: 2, i + 1: 2, i + 2: 2}) for i in range(1, 8))
_all_chows_t = tuple(Counter({i: 3, i + 1: 3, i + 2: 3}) for i in range(1, 8))
_all_chows_q = tuple(Counter({i: 4, i + 1: 4, i + 2: 4}) for i in range(1, 8))


def get_eyes(i):
    """
    >>> get_eyes(1)
    Counter({1: 2})
    """
    return _all_eyes[i - 1]

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


def classify_suit_tiles(tiles):
    """Classify numbered tiles

    ``tiles`` must be an ordered sequence.
    """

    assert tiles
    work_tiles = tiles[:]

    if (ntile := len(work_tiles)) == 1:
        return {TileTupleType.ISOLATED: (work_tiles[0],)}

    if ntile == 2:
        return {_classify_pair(work_tiles): work_tiles}

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
        type_front = _classify_pair(work_tiles[:2])
        type_back = _classify_pair(work_tiles[1:])

        if type_front == type_back == TileTupleType.ISOLATED:
            return {TileTupleType.ISOLATED: work_tiles}

        return {
            {
                type_front: work_tiles[:2],
                TileTupleType.ISOLATED: work_tiles[-1],
            },
            {
                TileTupleType.ISOLATED: work_tiles[0],
                type_back: work_tiles[1:],
            },}


def _classify_pair(tiles):
    """A helper function"""

    assert len(tiles) == 2
    diff = tiles[1] - tiles[0]

    if diff == 0:
        return TileTupleType.SIMPLE_PAIR
    if diff == 1:
        return TileTupleType.SERIAL_PAIR
    if diff == 2:
        if tiles[0] == 1 or tiles[-1] == 9:
            return TileTupleType.TERMINAL_SERIAL_PAIR
        return TileTupleType.SEPARATED_SERIAL_PAIR
    return TileTupleType.ISOLATED


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


def decouple_eye(tiles):
    """Decouple simple pairs from tiles

    >>> g = decouple_eye([1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9])
    >>> for pattern in g:
    ...     print(pattern)
    ...
    (1, [1, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9])
    (9, [1, 1, 1, 2, 3, 4, 5, 6, 7, 8, 9])

    """

    for i in range(1, 10):
        counter = Counter(tiles)
        if counter[i] >= 2:
            counter[i] -= 2
            yield i, list(counter.elements())


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


def resolve_melds_demo():
    """WIP"""

    player_hand = Counter([3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6])
    resolve_melds_single_wait(player_hand)
    for tile in player_hand.keys():
        if player_hand[tile] >= 2:
            eyes = get_eyes(tile)
            resolve_melds_with_eyes(player_hand - eyes, eyes)


#resolve_melds_demo()


# Features for seven pairs

def resolve_melds_seven_pairs(player_hand):
    """Resolve all the waiting tiles as Seven Pairs.

    Note that Seven Pairs must be of seven different pairs. Two identical pairs
    are not allowed.

    >>> resolve_melds_seven_pairs(Counter('AABBCCDDEEFFG'))
    (0, ('G',))
    >>> resolve_melds_seven_pairs(Counter('AABBCCDDEEFGH'))
    (1, ('F', 'G', 'H'))

    A hand with four different pairs is 2-shanten of Seven Pairs:

    >>> resolve_melds_seven_pairs(Counter('AAABBBCCCDDEF'))
    (2, ('E', 'F'))
    >>> resolve_melds_seven_pairs(Counter('AABBCCDDEFGHI'))
    (2, ('E', 'F', 'G', 'H', 'I'))

    >>> resolve_melds_seven_pairs(Counter('AABBCCCCDEFGH'))
    (3, ('D', 'E', 'F', 'G', 'H'))
    >>> shanten, tiles = resolve_melds_seven_pairs(Counter('ABCDEFabcdef0'))
    >>> shanten, len(tiles)
    (6, 13)
    """

    assert isinstance(player_hand, Counter)

    npair = sum(1 for v in player_hand.values() if v >= 2)
    waiting_tiles = tuple(
        tile for tile in player_hand if player_hand[tile] < 2)

    return 6 - npair, waiting_tiles


# Features for Thirteen Orphans

def resolve_melds_thirteen_orphans(player_hand):
    """Resolve all the waiting tiles as Thirteen Orphans.
    """
