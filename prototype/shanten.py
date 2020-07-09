#!/usr/bin/env python

"""
mahjan.shanten
"""

from collections import Counter
import sys
from typing import Iterable, Tuple, Union

import tiles


def count_shanten_std(player_hand: Union[Counter, Iterable]) -> int:
    """Count the shanten number of player's hand to 4-melds-1-pair form.

    >>> count_shanten_std(tiles.tiles('3899m3457p88s南白発'))
    4
    >>> count_shanten_std(tiles.tiles('3899m3457p88s南発発'))
    3
    >>> count_shanten_std(tiles.tiles('389m3457p888s南発発'))
    2
    >>> count_shanten_std(tiles.tiles('89m23457p888s南発発'))
    1
    >>> count_shanten_std(tiles.tiles('88m23457p888s南発発'))
    1

    >>> count_shanten_std(tiles.tiles('112233m258p39s西中'))
    4

    >>> count_shanten_std(tiles.tiles('1289m1289p1289s北'))
    4

    >>> count_shanten_std(tiles.tiles('5566m3477p56s'))
    2
    >>> count_shanten_std(tiles.tiles('566m77p56s'))
    1
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    num_tile = sum(player_hand.values())
    if num_tile % 3 != 1:
        raise ValueError('the number of tiles muse be 3n + 1.')

    if num_tile == 1:
        # Obvious tempai.
        return 0

    part_m = player_hand & tiles.FILTER_CHARACTERS
    part_p = player_hand & tiles.FILTER_CIRCLES
    part_s = player_hand & tiles.FILTER_BAMBOOS
    part_m, part_p, part_s = (tiles.convert_suit_to_number(suit_part)
                              for suit_part in (part_m, part_p, part_s))

    melds_m, melds_p, melds_s = (
        remove_melds(suit_part, tiles. MELDS_NUMBER) for suit_part in (
            part_m, part_p, part_s))
    pairs_m, pairs_p, pairs_s = (
        remove_pairs(suit_part, tiles.PAIRS_NUMBER) for suit_part in (
            part_m, part_p, part_s))

    hand_h = player_hand & tiles.FILTER_HONORS
    melds_h = remove_melds(hand_h, tiles.MELDS_HONOR)
    pairs_h = remove_pairs(hand_h, tiles.PAIRS_HONOR)

    # 13, 10, 7, 4, 1 -> 8, 6, 4, 2, 0
    num_shanten = (num_tile - 1) // 3 * 2
    num_shanten -= sum(len(melds) for melds in (
        melds_m, melds_p, melds_s, melds_h)) * 2
    num_shanten -= min(4, sum(len(pairs) for pairs in (
        pairs_m, pairs_p, pairs_s, pairs_h)))

    return num_shanten


def remove_melds(player_hand: Counter, all_melds: Tuple) -> Tuple[Counter]:
    """Remove some melds from player's hand.

    >>> remove_melds(Counter([3, 8, 9, 9]), MELDS_NUMBER)
    ()
    >>> remove_melds(Counter([3, 4, 5, 7]), MELDS_NUMBER)
    (Counter({3: 1, 4: 1, 5: 1}),)
    >>> remove_melds(Counter([8, 8]), MELDS_NUMBER)
    ()

    If duplicate melds are contained in player's hand, all of them will be
    removed from the hand.

    >>> remove_melds(Counter([1, 1, 2, 2, 3, 3]), MELDS_NUMBER)
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

    >>> remove_pairs(Counter([3, 8, 9, 9]), _all_pairs_suit)
    (Counter({8: 1, 9: 1}),)

    >>> remove_pairs(Counter([7]), _all_pairs_suit)
    ()

    >>> remove_pairs(Counter([8, 8]), _all_pairs_suit)
    (Counter({8: 2}),)

    >>> remove_pairs(Counter({5: 2, 6: 2}), _all_pairs_suit)
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


if __name__ == '__main__':
    print(count_shanten_std(tiles.tiles(sys.argv[1])))
