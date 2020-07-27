"""
mahjong.melds

<Melds are groups of tiles within the player's hand, consisting of either a Pong
(three identical tiles), a Kong (four identical tiles), a Chow (three Simple
tiles all of the same suit, in numerical sequence)>(Mahjong - Wikipedia)
"""

from collections import Counter
from enum import Enum
from typing import Tuple

import tiles

class DiscardedBy(Enum):
    """Positions of the player that discarded the tile claimed"""

    LEFT = '上家'
    CENTER = '対面'
    RIGHT = '下家'


class Meld:
    """Base class"""

    def __init__(self, tileinfo, concealed: bool, discarded_by: DiscardedBy):
        self.tileinfo = tileinfo
        self.concealed = concealed
        self.discarded_by = discarded_by

    def __str__(self):
        return f'{self.__class__.__name__}({self.tileinfo}, {self.concealed}, {self.discarded_by})'


class Chow(Meld):
    """Chow"""

    def __init__(self, tileinfo, concealed: bool):
        super().__init__(tileinfo, concealed, DiscardedBy.LEFT)


    @property
    def minipoints(self):
        """Return the value of minipoints (fu)"""
        return 0


class Pung(Meld):
    """Pung"""

    _minipoints_base = 2

    @property
    def minipoints(self):
        """Return the value of minipoints (fu)"""
        value = self._minipoints_base
        if self.concealed:
            value <<= 1
        if not tiles.is_simple(self.tileinfo):
            value <<= 1
        return value

    def extend_to_kong(self):
        """加槓"""
        return Kong(self.tileinfo, False, self.discarded_by)


class Kong(Pung):
    """Kong"""

    _minipoints_base = 8


def is_pair_eyes(pair: Counter) -> bool:
    """Test if a pair is eyes

    >>> is_pair_eyes(Counter({8: 2}))
    True
    """

    return len(pair) == 1 and sum(pair.values()) == 2


def remove_melds(player_hand: Counter, all_melds: Tuple) -> Tuple[Counter]:
    """Remove some melds from player's hand.

    >>> remove_melds(Counter([3, 8, 9, 9]), tiles.MELDS_NUMBER)
    ()
    >>> remove_melds(Counter([3, 4, 5, 7]), tiles.MELDS_NUMBER)
    (Counter({3: 1, 4: 1, 5: 1}),)
    >>> remove_melds(Counter([8, 8]), tiles.MELDS_NUMBER)
    ()

    If duplicate melds are contained in player's hand, all of them will be
    removed from the hand.

    >>> remove_melds(Counter([1, 1, 2, 2, 3, 3]), tiles.MELDS_NUMBER)
    (Counter({1: 1, 2: 1, 3: 1}), Counter({1: 1, 2: 1, 3: 1}))
    """

    remains = sum(player_hand.values())
    melds = []
    for meld in all_melds:
        while player_hand & meld == meld:
            player_hand -= meld
            remains -= 3
            melds.append(meld)
            if remains < 3:
                break

        if remains < 3:
            break

    return tuple(melds)


def remove_pairs(player_hand: Counter, all_pairs: Tuple) -> Tuple[Counter]:
    """Remove some pairs as incomplete melds from player's hand.

    >>> remove_pairs(Counter([3, 8, 9, 9]), tiles.PAIRS_NUMBER)
    (Counter({8: 1, 9: 1}),)

    >>> remove_pairs(Counter([7]), tiles.PAIRS_NUMBER)
    ()

    >>> remove_pairs(Counter([8, 8]), tiles.PAIRS_NUMBER)
    (Counter({8: 2}),)

    >>> remove_pairs(Counter({5: 2, 6: 2}), tiles.PAIRS_NUMBER)
    (Counter({5: 2}), Counter({6: 2}))
    """

    remains = sum(player_hand.values())
    pairs = []
    for pair in all_pairs:
        while player_hand & pair == pair:
            player_hand -= pair
            remains -= 2
            pairs.append(pair)
            if remains < 2:
                break

        if remains < 2:
            break

    return tuple(pairs)
