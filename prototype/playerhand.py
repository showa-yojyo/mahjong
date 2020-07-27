#!/usr/bin/env python

"""
mahjong.playerhand
"""

from collections import Counter

from melds import (DiscardedBy, Chow, Pung, Kong)
from shanten import (
    count_shanten_13_orphans,
    count_shanten_seven_pairs,
    count_shanten_std)
import tiles
from walls import TileWallAgent


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

        self.shanten_std, self.shanten_7, self.shanten_13 = None, None, None
        if initial_update:
            self.update()


    def __str__(self):
        # concealed part
        concealed_part = tiles.format_tiles(self.concealed_part.elements())

        # exposed part
        exposed_part = ' '.join(str(meld) for meld in self.exposed_parts)
        return f'{concealed_part} {exposed_part} {self.shanten} シャンテン'


    @property
    def is_concealed(self) -> bool:
        """Determine if all the tile is concealed."""
        # return not self._exposed
        return sum(self.concealed_part.values()) == 13

    @property
    def concealed_part(self):
        """Return concealed tiles."""
        return self._concealed

    def get_concealed_part_by_class(self, tile_class) -> Counter:
        """Return the part that consists of specific tiles"""

        return self.concealed_part & tiles.get_filter(tile_class)

    @property
    def exposed_parts(self):
        """Return exposed melds."""
        return self._exposed

    @property
    def shanten(self):
        """Return the shanten number"""
        if not self.is_concealed:
            return self.shanten_std

        return min(self.shanten_std, self.shanten_7, self.shanten_13)

    def can_claim_chow(self, discarded_tile: tiles.Tile) -> bool:
        """Test if the player can claim for a Chow

        >>> [PlayerHand('12m東南').can_claim_chow(
        ...  tiles.tiles('3{}'.format(i))) for i in 'mps']
        [True, False, False]

        >>> [PlayerHand('89m東南').can_claim_chow(
        ...  tiles.tiles('7{}'.format(i))) for i in 'mps']
        [True, False, False]

        >>> [PlayerHand('35p東南').can_claim_chow(
        ...  tiles.tiles('4{}'.format(i))) for i in 'mps']
        [False, True, False]

        >>> [PlayerHand('4567m').can_claim_chow(
        ...  tiles.tiles('{}m'.format(i))) for i in range(1, 10)]
        [False, False, True, True, True, True, True, True, False]

        >>> any(PlayerHand('258p西').can_claim_chow(
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

        >>> hand = PlayerHand('9m66s2p発発発')
        >>> hand.can_claim_pung(tiles.tiles('6s'))
        True
        >>> hand.can_claim_pung(tiles.tiles('発'))
        True

        >>> PlayerHand('149m6s白発中').can_claim_pung(tiles.tiles('発'))
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
        >>> PlayerHand('9m66s2p発発発').can_claim_kong(tiles.tiles('発'))
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
        >>> player_hand.concealed_part[tile1]
        1
        >>> player_hand.concealed_part[target_tile]
        1
        >>> player_hand.concealed_part[tile2]
        0
        """

        self.exposed_parts.append(Chow([new_tile, tile1, tile2], False))
        self.concealed_part.subtract([tile1, tile2])
        # self.update()

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
        >>> player_hand.concealed_part[target_tile]
        0
        """

        self.exposed_parts.append(Pung(tile, False, discarded_by))
        self.concealed_part.subtract({tile: 2})
        # self.update()

    def commit_kong(self, tile: tiles.Tile, discarded_by: DiscardedBy):
        """Add/extend a Kong.

        Determine if the claiming for this Kong is a melded, concealed or
        extension Kong by this hand and ``discarded_by``.

        Example 1: 大明槓

        >>> hand = PlayerHand(tiles.tiles('479m378p568s東東東白'))
        >>> hand.commit_kong(tiles.tiles('東'), DiscardedBy.CENTER)
        >>> hand.concealed_part - Counter(tiles.tiles('479m378p568s白'))
        Counter()
        >>> kong = hand.exposed_parts[-1]
        >>> print(kong.discarded_by)
        DiscardedBy.CENTER

        Example 2: 暗槓

        >>> hand = PlayerHand(tiles.tiles('479m378p568s東東東東'))
        >>> hand.commit_kong(tiles.tiles('東'), None)
        >>> hand.concealed_part - Counter(tiles.tiles('479m378p568s'))
        Counter()
        >>> kong = hand.exposed_parts[-1]
        >>> print(kong.discarded_by)
        None

        Example 3: 加槓

        >>> hand = PlayerHand(tiles.tiles('479m378p568s白'),
        ...                   [Pung(tiles.tiles('東'), True, DiscardedBy.RIGHT)])
        >>> hand.commit_kong(tiles.tiles('東'), None)
        >>> kong = hand.exposed_parts[-1]
        >>> isinstance(kong, Kong)
        True
        >>> kong.tileinfo == tiles.tiles('東')
        True
        >>> print(kong.discarded_by)
        DiscardedBy.RIGHT
        """

        if discarded_by:
            # A melded Kong
            self.exposed_parts.append(Kong(tile, False, discarded_by))
            self.concealed_part.subtract({tile: 3})
        elif self.concealed_part.get(tile, 0) == 4:
            # A concealed Kong
            self.exposed_parts.append(Kong(tile, True, None))
            self.concealed_part.subtract({tile: 4})
        else:
            # A melded Pung is extended to a melded Kong
            for i, meld in enumerate(self.exposed_parts):
                if meld.tileinfo == tile:
                    self._exposed[i] = meld.extend_to_kong()
                    break

        # Note: リンシャンから補充するまで self.update_shanten() を呼べない
        # self.update()

    def update(self):
        """Update internal state"""
        self.update_claimable_tiles()
        self.update_shanten()

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
                         self.concealed_part & tiles.FILTER_CHARACTERS)
        _find_mate_pairs(tiles.TILE_RANGE_CIRCLES,
                         self.concealed_part & tiles.FILTER_CIRCLES)
        _find_mate_pairs(tiles.TILE_RANGE_BAMBOOS,
                         self.concealed_part & tiles.FILTER_BAMBOOS)

        self.claimable_chow = claimable_chow

    def update_claimable_tiles_pung(self):
        """Update information for claiming a Pung.

        >>> player_hand = PlayerHand('26m334568p38s東発発')
        >>> player_hand.update_claimable_tiles_pung()
        >>> set(tiles.tiles('3p発')) == player_hand.claimable_pung
        True
        """

        counter = self.concealed_part
        self.claimable_pung = set(
            tile for tile in counter if counter[tile] >= 2)

    def update_claimable_tiles_kong(self):
        """Update information for claiming a Kong.

        >>> player_hand = PlayerHand('26m333368p38s発発発')
        >>> player_hand.update_claimable_tiles_kong()
        >>> set(tiles.tiles('3p発')) == player_hand.claimable_kong
        True
        """

        counter = self.concealed_part

        # 大明槓 or 暗槓
        self.claimable_kong = set(
            tile for tile in counter if counter[tile] in (3, 4))

        # 加槓
        self.claimable_kong.union(
            meld.tileinfo for meld in self.exposed_parts
            if isinstance(meld, Pung))

    def update_shanten(self):
        """Update the shanten number"""

        player_hand = self.concealed_part
        self.shanten_std = count_shanten_std(player_hand)
        if self.is_concealed:
            self.shanten_7 = count_shanten_seven_pairs(player_hand)
            self.shanten_13 = count_shanten_13_orphans(player_hand)
        else:
            self.shanten_7 = None
            self.shanten_13 = None


def main():
    """test"""

    wall_agent = TileWallAgent()
    player_hands = [PlayerHand(Counter(ph)) for ph in wall_agent.build()]
    for player_hand in player_hands:
        print(player_hand)

if __name__ == '__main__':
    main()
