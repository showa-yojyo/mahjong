"""
mahjong.playerhand
"""

from collections import Counter
from enum import Enum

import tiles

class DiscardedBy(Enum):
    """Position of the player that discarded the tile"""

    LEFT = '上家'
    CENTER = '対面'
    RIGHT = '下家'


class Meld:
    """Base class"""

    def __init__(self, tileinfo, concealed: bool, discarded_by: DiscardedBy):
        self.tileinfo = tileinfo
        self.concealed = concealed
        self.discarded_by = discarded_by


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

    def __str__(self):
        return f'{self.__class__.__name__}({self.tileinfo}, {self.concealed}, {self.discarded_by})'

    @property
    def minipoints(self):
        """Return the value of minipoints (fu)"""
        value = self._minipoints_base
        if self.concealed:
            value <<= 1
        if not tiles.is_simple(self.tileinfo):
            value <<= 1
        return value


class Kong(Pung):
    """Kong"""

    _minipoints_base = 8


class PlayerHand:
    """Player's hand."""

    def __init__(self, concealed, exposed=None):
        if isinstance(concealed, str):
            concealed = tiles.tiles(concealed)

        if isinstance(concealed, Counter):
            self._concealed = concealed
        else:
            self._concealed = Counter(concealed)
        self._exposed = exposed or []

    @property
    def is_concealed(self) -> bool:
        """Determine if all the tile is concealed."""
        return not self._exposed

    @property
    def concealed_parts(self):
        """Return concealed tiles."""
        return self._concealed

    def get_concealed_part_by_class(self, tile_class) -> Counter:
        """Return the part that consists of specific tiles"""

        return self.concealed_parts & tiles.get_filter(tile_class)

    @property
    def exposed_parts(self):
        """Return exposed melds."""
        return self._exposed


    def can_claim_chow(self, discarded_tile: tiles.Tile) -> bool:
        """Test if the player can claim for a Chow

        >>> [PlayerHand('12m').can_claim_chow(
        ...  tiles.tiles('3{}'.format(i))) for i in 'mps']
        [True, False, False]

        >>> [PlayerHand('89m').can_claim_chow(
        ...  tiles.tiles('7{}'.format(i))) for i in 'mps']
        [True, False, False]

        >>> [PlayerHand('35p').can_claim_chow(
        ...  tiles.tiles('4{}'.format(i))) for i in 'mps']
        [False, True, False]

        >>> [PlayerHand('4567m').can_claim_chow(
        ...  tiles.tiles('{}m'.format(i))) for i in range(1, 10)]
        [False, False, True, True, True, True, True, True, False]

        >>> any(PlayerHand('258p').can_claim_chow(
        ...     tiles.tiles('{}p'.format(i))) for i in range(1, 10))
        False

        >>> all(PlayerHand('1112345678999s').can_claim_chow(
        ...     tiles.tiles('{}s'.format(i))) for i in range(1, 10))
        True
        """

        if len(self.concealed_parts) == 1:
            return False

        tile_class = tiles.get_tile_class(discarded_tile)
        if tile_class == tiles.TileClass.HONOR:
            return False

        target_tiles = self.get_concealed_part_by_class(tile_class)

        numm1 = discarded_tile - 1 in target_tiles
        nump1 = discarded_tile + 1 in target_tiles
        if not numm1 and not nump1:
            return False

        if numm1:
            return discarded_tile - 2 in target_tiles or nump1
        if nump1:
            return discarded_tile + 2 in target_tiles

        return False


    def can_claim_pung(self, discarded_tile: tiles.Tile):
        """Test if the player can claim for a Pung.

        >>> PlayerHand('149m66s発発').can_claim_pung(tiles.tiles('発'))
        True
        >>> PlayerHand('9m66s発発発').can_claim_pung(tiles.tiles('発'))
        True

        >>> PlayerHand('149m66s白発中').can_claim_pung(tiles.tiles('発'))
        False
        >>> [PlayerHand('1112345678999m').can_claim_pung(
        ...  tiles.tiles(f'{i}m')) for i in range(1, 10)]
        [True, False, False, False, False, False, False, False, True]
        """

        return self.concealed_parts.get(discarded_tile, 0) >= 2


    def can_claim_kong(self, target_tile: tiles.Tile):
        """Test if the player can claim for a Kong (melded or concealed).

        >>> PlayerHand('149m66s発発').can_claim_kong(tiles.tiles('発'))
        False
        >>> PlayerHand('9m66s発発発').can_claim_kong(tiles.tiles('発'))
        True
        """

        return self.concealed_parts.get(target_tile, 0) >= 3


    # TODO: 加槓


    def commit_chow(
            self,
            new_tile: tiles.Tile,
            tile1: tiles.Tile,
            tile2: tiles.Tile):
        """Add a Chow to the exposed part.

        >>> player_hand = PlayerHand('12457789m45p346s')
        >>> target_tile = tiles.tiles('8m')
        >>> tile1, tile2 = tiles.tiles('7m'), tiles.tiles('9m')
        >>> player_hand.commit_chow(target_tile, tile1, tile2)
        >>> chow = player_hand.exposed_parts[0]
        >>> isinstance(chow, Chow)
        True
        >>> chow.concealed
        False
        >>> print(chow.discarded_by)
        DiscardedBy.LEFT
        >>> player_hand.concealed_parts[tile1]
        1
        >>> player_hand.concealed_parts[target_tile]
        1
        >>> player_hand.concealed_parts[tile2]
        0
        """

        self.exposed_parts.append(Chow([new_tile, tile1, tile2], False))
        self.concealed_parts.subtract([tile1, tile2])


    def commit_pung(self, tile: tiles.Tile, discarded_by: DiscardedBy):
        """Add a Pung to the exposed part.

        >>> player_hand = PlayerHand('2457789m248p14s白')
        >>> target_tile = tiles.tiles('7m')
        >>> player_hand.commit_pung(target_tile, DiscardedBy.CENTER)
        >>> pung = player_hand.exposed_parts[0]
        >>> assert isinstance(pung, Pung)
        >>> assert pung.tileinfo == target_tile
        >>> pung.concealed
        False
        >>> print(pung.discarded_by)
        DiscardedBy.CENTER
        >>> player_hand.concealed_parts[target_tile]
        0
        """

        self.exposed_parts.append(Pung(tile, False, discarded_by))
        self.concealed_parts.subtract({tile: 2})
