"""
PROTOTYPE

Grossary:

* Pair: 対子・雀頭
* Serial pair: 両面搭子
* Separated serial pair: 嵌張搭子
* Terminal serial pair: 辺張搭子
"""

from collections import Counter
from itertools import combinations_with_replacement

_bad_numbers = {-1, 0, 10, 11}

def _bounds(nlower, nupper):
    """
    >>> _bounds(1, 2)
    (1, 2)
    >>> _bounds(2, 1)
    (1, 2)
    """

    if nlower > nupper:
        nlower, nupper = nupper, nlower
    return (nlower, nupper)

def clip(num):
    """Clip a number to between 1 and 9

    >>> clip(0)
    1
    >>> clip(10)
    9
    >>> clip(5)
    5
    """

    return max(1, min(9, num))


# Resolvers for tempai of four tiles


def resolve_waiting_4(tiles):
    """Resolve all the waiting tiles of four tiles.

    ``tiles`` must be a sequence and ordered.

    >>> resolve_waiting_4([5] * 4) == (1, {3, 4, 6, 7})
    True
    >>> resolve_waiting_4([1] * 4) == (1, {2, 3})
    True
    >>> resolve_waiting_4([9] * 4) == (1, {7, 8})
    True

    Two different pairs:

    >>> resolve_waiting_4([1, 1, 2, 2]) == (0, {1, 2})
    True

    >>> resolve_waiting_4([1, 1, 2, 3]) == (0, {1, 4})
    True
    >>> resolve_waiting_4([1, 1, 5, 6]) == (0, {4, 7})
    True
    >>> resolve_waiting_4([1, 1, 5, 7]) == (0, {6})
    True
    >>> resolve_waiting_4([1, 1, 5, 9]) == (1, {3, 4, 5, 6, 7, 8, 9})
    True
    >>> resolve_waiting_4([1, 1, 8, 9]) == (0, {7})
    True
    >>> resolve_waiting_4([1, 2, 2, 3]) == (0, {2})
    True
    >>> resolve_waiting_4([1, 2, 3, 3]) == (0, {3})
    True
    """

    assert len(tiles) == 4
    bag = Counter(tiles)

    if (ntype := len(bag)) == 1:
        # Not a kong but a Pong and a single
        return (1, _resolve_isolated_number(tiles[0], False))

    if ntype == 2:
        # On tempai
        if set(bag.values()) == {3, 1}:
            return resolve_waiting_aaab(tiles, bag)

        # A double-Pong waiting
        return (0, set(bag.keys()))

    if ntype == 3:
        # AABC pattern
        # Frequency: 2, 1, 1.
        _, second1, second2 = bag.most_common(ntype)
        nlower, nupper = _bounds(second1[0], second2[0])
        tiles = _resolve_waiting_for_chow(nlower, nupper)
        if tiles:
            # Tempai
            return (0, tiles)

        # 1 shanten
        waiting_tiles = _resolve_isolated_number(nlower, True)
        waiting_tiles |= _resolve_isolated_number(nupper, True)
        return (1, waiting_tiles)

    # ABCD pattern
    return resolve_waiting_abcd(tiles)


def resolve_waiting_aaab(tiles, bag=None):
    """Resolve whether multiple or single waiting.

    >>> resolve_waiting_aaab([4, 4, 4, 5]) == (0, {3, 6, 5})
    True
    >>> resolve_waiting_aaab([4, 5, 5, 5]) == (0, {3, 6, 4})
    True
    >>> resolve_waiting_aaab([1, 1, 1, 2]) == (0, {2, 3})
    True
    >>> resolve_waiting_aaab([1, 2, 2, 2]) == (0, {1, 3})
    True
    >>> resolve_waiting_aaab([8, 8, 8, 9]) == (0, {7, 9})
    True
    >>> resolve_waiting_aaab([8, 9, 9, 9]) == (0, {7, 8})
    True
    >>> resolve_waiting_aaab([1, 1, 1, 9]) == (1, {9})
    True
    >>> resolve_waiting_aaab([2, 8, 8, 8]) == (1, {2})
    True
    """

    assert len(tiles) == 4

    if not bag:
        bag = Counter(tiles)

    _, second = bag.most_common(2)
    # case 1: A single wait and a Pong
    waiting_tiles = {second[0]}

    # case 2: Two pairs?
    waiting_tiles_serial = _resolve_waiting_for_chow(*bag.keys())
    if waiting_tiles_serial:
        waiting_tiles |= waiting_tiles_serial
        return (0, waiting_tiles)

    return (1, waiting_tiles)


def resolve_waiting_abcd(tiles):
    """Resolve all the waiting tiles of ABCD pattern.

    >>> resolve_waiting_4([1, 2, 3, 4]) == (0, {1, 4})
    True
    >>> resolve_waiting_4([3, 4, 5, 6]) == (0, {3, 6})
    True
    >>> resolve_waiting_4([6, 7, 8, 9]) == (0, {6, 9})
    True
    >>> resolve_waiting_4([1, 7, 8, 9]) == (0, {1})
    True

    >>> resolve_waiting_4([1, 4, 8, 9])
    (1, {1, 4, 7})
    >>> resolve_waiting_4([1, 2, 8, 9])
    (1, {1, 2, 3, 7, 8, 9})
    >>> resolve_waiting_4([1, 3, 5, 7])
    (1, {1, 2, 3, 4, 5, 6, 7})
    >>> resolve_waiting_4([2, 4, 6, 8])
    (1, {2, 3, 4, 5, 6, 7, 8})
    """

    assert len(set(tiles)) == 4

    waiting_tiles = set()
    seq_diff = [tiles[i + 1] - tiles[i] for i in range(0, 3)]

    # Case of BCD is a Chow
    if seq_diff[1] == seq_diff[2] == 1:
        waiting_tiles.add(tiles[0])

    # Case of ABC is a Chow
    if seq_diff[0] == seq_diff[1] == 1:
        waiting_tiles.add(tiles[-1])

    if waiting_tiles:
        # On tempai
        return (0, waiting_tiles)

    # Case of AB, BC, CD is a tower
    # A tower and two isolated tiles
    for i in range(3):
        welcome = _resolve_waiting_for_chow(
            tiles[i], tiles[i + 1])
        if welcome:
            waiting_tiles |= welcome
            waiting_tiles.add(tiles[i - 1])
            waiting_tiles.add(tiles[(i + 2) % 4])

    return (1, waiting_tiles)


def _resolve_isolated_number(num, allow_pair=True):
    """Return all the numbers that make a tower with the number ``num``.

    >>> _resolve_isolated_number(1) == {1, 2, 3}
    True
    >>> _resolve_isolated_number(1, False) == {2, 3}
    True
    >>> _resolve_isolated_number(5) == {3, 4, 5, 6, 7}
    True
    >>> _resolve_isolated_number(5, False) == {3, 4, 6, 7}
    True
    >>> _resolve_isolated_number(9) == {7, 8, 9}
    True
    >>> _resolve_isolated_number(9, False) == {7, 8}
    True
    """

    welcome_numbers = set(range(num - 2, num + 2 + 1))
    welcome_numbers -= _bad_numbers
    if not allow_pair:
        welcome_numbers.remove(num)

    return welcome_numbers


def _resolve_waiting_for_chow(nlower, nupper):
    """Return one or two tiles that make a Chow along with the
    two numbers.

    >>> _resolve_waiting_for_chow(1, 2) == {3}
    True
    >>> _resolve_waiting_for_chow(8, 9) == {7}
    True
    >>> _resolve_waiting_for_chow(1, 3) == {2}
    True
    >>> _resolve_waiting_for_chow(7, 9) == {8}
    True
    >>> _resolve_waiting_for_chow(5, 6) == {4, 7}
    True
    >>> not _resolve_waiting_for_chow(3, 3)
    True
    >>> not _resolve_waiting_for_chow(1, 9)
    True
    """

    if nlower > nupper:
        nlower, nupper = nupper, nlower

    if (diff := nupper - nlower) == 1:
        # A two-sided waiting a.k.a. (normal) serial pair
        # An edge waiting a.k.a. terminal serial pair
        return {nlower - 1, nupper + 1} - _bad_numbers
    elif diff == 2:
        # A closed waiting a.k.a separated serial pair
        return {nlower + 1}
    else:
        return None


def make_resolver_table_4():
    """Construct the look-up table for 4 numbered tiles"""

    return {
        tiles: resolve_waiting_4(tiles)
        for tiles in combinations_with_replacement(range(1, 10), 4)}


def resolve_waiting_7(tiles):
    """Resolve all waiting tiles of seven numbered tiles.

    ``tiles`` must be an ordered sequence.
    """

    assert len(tiles) == 7
