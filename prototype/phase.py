"""
mahjong.phase
"""

from winds import (Winds, get_right_wind)

class Phase:
    """東一局一本場 etc.

    >>> hand = Phase(Winds.EAST, 1, 0)
    >>> print(hand)
    東一局
    """

    def __init__(self, wind: Winds, hand: int, counter: int):
        assert 1 <= hand <= 4
        self.prevalent_wind = wind
        self.hand = hand
        self.counter = counter

    def __repr__(self):
        return f'Phase({self.prevalent_wind!r}, {self.hand}, {self.counter})'

    def __str__(self):
        name = f'{self.prevalent_wind!s}{"_一二三四"[self.hand]}局'
        if self.counter:
            return name + f' {self.counter} 本場'

        return name

    def proceed(self, update_dealer: bool, increment_counter: bool):
        """Go to the next hand.

        >>> hand = Phase(Winds.EAST, 1, 0)
        >>> hand.proceed(False, True)
        >>> print(hand)
        東一局 1 本場
        >>> hand.proceed(True, False)
        >>> print(hand)
        東二局
        >>> hand.proceed(True, True)
        >>> print(hand)
        東三局 1 本場

        >>> hand = Phase(Winds.EAST, 4, 0)
        >>> hand.proceed(True, False)
        >>> print(hand)
        南一局
        """

        if update_dealer:
            if self.hand != 4:
                self.hand += 1
            else:
                self.prevalent_wind = get_right_wind(self.prevalent_wind)
                self.hand = 1
        if increment_counter:
            self.counter += 1
        else:
            self.counter = 0
