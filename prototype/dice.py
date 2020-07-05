"""
mahjong.dice: Provides dice operations.
"""

import random

def toss(ndice=2):
    """The dealer throws n dice to decide the location where the gate of walls

    >>> dice = toss()
    >>> assert 2 <= dice[0] + dice[1] <= 12
    >>> random.seed(0xFFFFFFFF) # for doctest
    >>> for _ in range(10):
    ...    toss()
    ...
    (6, 5)
    (2, 2)
    (5, 5)
    (3, 5)
    (3, 4)
    (6, 6)
    (3, 3)
    (4, 4)
    (1, 2)
    (5, 2)
    """

    return tuple(random.randrange(1, 7) for _ in range(ndice))
