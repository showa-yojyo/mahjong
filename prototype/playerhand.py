"""
mahjong.playerhand
"""

from collections import Counter

import tiles


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


    def can_claim_chow(self, discarded_tile: int) -> bool:
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

        suit_tiles = self.get_concealed_part_by_class(tile_class)
        numbers = tiles.convert_suit_to_number(suit_tiles)
        number = tiles.get_suit_number(discarded_tile)

        numm1 = number - 1 in numbers
        nump1 = number + 1 in numbers
        if not numm1 and not nump1:
            return False

        if numm1:
            return number - 2 in numbers or nump1
        if nump1:
            return number + 2 in numbers

        return False


    def can_claim_pung(self, discarded_tile: int):
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


    def can_claim_kong(self, target_tile: int):
        """Test if the player can claim for a Kong (melded or concealed).

        >>> PlayerHand('149m66s発発').can_claim_kong(tiles.tiles('発'))
        False
        >>> PlayerHand('9m66s発発発').can_claim_kong(tiles.tiles('発'))
        True
        """

        return self.concealed_parts.get(target_tile, 0) >= 3


    # TODO: 加槓
