"""
Module mahjong.winds
"""

from enum import IntEnum
from typing import Tuple

class Winds(IntEnum):
    """Enumeration for winds
    """

    EAST = 0
    SOUTH = 1
    WEST = 2
    NORTH = 3


    def __bool__(self) -> bool:
        """Test if this wind is East

        >>> bool(Winds.EAST)
        True
        >>> bool(Winds.SOUTH)
        False
        >>> bool(Winds.WEST)
        False
        >>> bool(Winds.NORTH)
        False
        """
        return self == Winds.EAST


    def __str__(self) -> str:
        """Return informal representation

        >>> print(Winds.EAST)
        東
        >>> print(Winds.SOUTH)
        南
        >>> print(Winds.WEST)
        西
        >>> print(Winds.NORTH)
        北
        """
        return '東南西北'[int(self.value)]


def get_left_wind(wind: Winds) -> Winds:
    """Return the left wind

    >>> print(get_left_wind(Winds.EAST))
    北
    """

    return Winds((wind.value - 1) % 4)

def get_right_wind(wind: Winds) -> Winds:
    """Return the right wind

    >>> print(get_right_wind(Winds.NORTH))
    東
    """

    return Winds((wind.value + 1) % 4)


def wind_from_dice(
    *, dice: Tuple[int, int] = None, dice_sum: int = None) -> Winds:
    """Return the wind that corresponds to dice

    >>> print(wind_from_dice(dice=(1, 1)))
    南
    >>> print(wind_from_dice(dice=(1, 2)))
    西
    >>> print(wind_from_dice(dice=(1, 3)))
    北
    >>> print(wind_from_dice(dice=(1, 4)))
    東
    >>> print(wind_from_dice(dice=(6, 6)))
    北
    """

    if dice and not dice_sum:
        dice_sum = sum(dice)

    return Winds((dice_sum - 1) % 4)
