"""
mahjong.playerhand
"""

from collections import Counter
from enum import Enum

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

    def __init__(self, concealed, exposed=None, initial_update=True):
        if isinstance(concealed, str):
            concealed = tiles.tiles(concealed)

        if isinstance(concealed, Counter):
            self._concealed = concealed
        else:
            self._concealed = Counter(concealed)
        self._exposed = exposed or []

        self.claimable_chow = {}
        self.claimable_pung = {}
        self.claimable_kong = {}
        self.claimable_win = {}
        if initial_update:
            self.update_claimable_tiles()

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

        return discarded_tile in self.claimable_chow

    def can_claim_pung(self, discarded_tile: tiles.Tile):
        """Test if the player can claim for a Pung.

        >>> hand = PlayerHand('149m66s発発')
        >>> hand.can_claim_pung(tiles.tiles('1s'))
        False
        >>> hand.can_claim_pung(tiles.tiles('6s'))
        True
        >>> hand.can_claim_pung(tiles.tiles('発'))
        True

        >>> hand = PlayerHand('9m66s発発発')
        >>> hand.can_claim_pung(tiles.tiles('6s'))
        True
        >>> hand.can_claim_pung(tiles.tiles('発'))
        True

        >>> PlayerHand('149m66s白発中').can_claim_pung(tiles.tiles('発'))
        False
        >>> [PlayerHand('1112345678999m').can_claim_pung(
        ...  tiles.tiles(f'{i}m')) for i in range(1, 10)]
        [True, False, False, False, False, False, False, False, True]
        """

        return discarded_tile in self.claimable_pung

    def can_claim_kong(self, target_tile: tiles.Tile):
        """Test if the player can claim for a Kong (melded or concealed).

        >>> PlayerHand('149m66s発発').can_claim_kong(tiles.tiles('発'))
        False
        >>> PlayerHand('9m66s発発発').can_claim_kong(tiles.tiles('発'))
        True
        """

        return target_tile in self.claimable_kong

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
        self.update_claimable_tiles()

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
        self.update_claimable_tiles()

    def update_claimable_tiles(self):
        """WIP"""
        self.update_claimable_tiles_chow()
        self.update_claimable_tiles_pung()
        self.update_claimable_tiles_kong()

    def update_claimable_tiles_chow(self):
        """Update information for claiming a Chow.

        >>> player_hand = PlayerHand('26m334568p38s東発発')
        >>> player_hand.update_claimable_tiles_chow()
        >>> set(tiles.tiles('234567p')) == player_hand.claimable_chow
        True
        """

        def _find_mate_pairs(suits, part):
            def _get_mate_pair(tile):
                yield (tile - 2, tile - 1)
                yield (tile - 1, tile + 1)
                yield (tile + 1, tile + 2)

            # XXX: 以下のループをなぜか comprehension で書けない？
            for tile in suits:
                if any(mate[0] in part and mate[1] in part
                       for mate in _get_mate_pair(tile)):
                    claimable_chow.add(tile)

        claimable_chow = set()
        _find_mate_pairs(tiles.TILE_RANGE_CHARACTERS,
                         self.concealed_parts & tiles.FILTER_CHARACTERS)
        _find_mate_pairs(tiles.TILE_RANGE_CIRCLES,
                         self.concealed_parts & tiles.FILTER_CIRCLES)
        _find_mate_pairs(tiles.TILE_RANGE_BAMBOOS,
                         self.concealed_parts & tiles.FILTER_BAMBOOS)

        self.claimable_chow = claimable_chow

    def update_claimable_tiles_pung(self):
        """Update information for claiming a Pung.

        >>> player_hand = PlayerHand('26m334568p38s東発発')
        >>> player_hand.update_claimable_tiles_pung()
        >>> set(tiles.tiles('3p発')) == player_hand.claimable_pung
        True
        """

        counter = self.concealed_parts
        self.claimable_pung = set(
            tile for tile in counter if counter[tile] >= 2)

    def update_claimable_tiles_kong(self):
        """Update information for claiming a Kong.

        >>> player_hand = PlayerHand('26m333368p38s発発発')
        >>> player_hand.update_claimable_tiles_kong()
        >>> set(tiles.tiles('3p発')) == player_hand.claimable_kong
        True
        """

        counter = self.concealed_parts

        # 大明槓 or 暗槓
        self.claimable_kong = set(
            tile for tile in counter if counter[tile] in (3, 4))

        # 加槓
        self.claimable_kong.union(
            meld.tileinfo for meld in self.exposed_parts
            if isinstance(meld, Pung))
