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


def count_shanten_13_orphans(player_hand: Union[Counter, Iterable]) -> int:
    """Count the shanten number of player's hand to Thirteen Orphans

    The length of ``players_hand`` must be 13 or 14.

    >>> count_shanten_13_orphans(tiles.tiles('139m19p19s東南西北白発中'))
    0
    >>> count_shanten_13_orphans(tiles.tiles('19m19p19s東南南西北白発中'))
    -1

    >>> count_shanten_13_orphans(tiles.tiles('17m133469p388s北発中')) # 9m19s東南西白
    7
    >>> count_shanten_13_orphans(tiles.tiles('17m133469p88s西北発中')) # 9m19s東南白
    6
    >>> count_shanten_13_orphans(tiles.tiles('11m133469p88s西北発中')) # 9m19s東南白
    5
    >>> count_shanten_13_orphans(tiles.tiles('119m13369p88s西北発中')) # 19s東南白
    4
    >>> count_shanten_13_orphans(tiles.tiles('119m1369p188s西北発中'))
    3
    >>> count_shanten_13_orphans(tiles.tiles('119m169p1889s西北発中'))
    2
    >>> count_shanten_13_orphans(tiles.tiles('119m19p1889s東西北発中'))
    1
    >>> count_shanten_13_orphans(tiles.tiles('119m19p189s東南西北発中'))
    0
    >>> count_shanten_13_orphans(tiles.tiles('119m19p19s東南西北発中'))
    0
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    if sum(player_hand.values()) not in (13, 14):
        raise ValueError('player_hand must be concealed')

    num_orphans = len(orphans := player_hand & tiles.THIRTEEN_ORPHANS)
    if (player_hand - orphans) & orphans:
        return 12 - num_orphans

    return 13 - num_orphans


def count_shanten_seven_pairs(player_hand: Union[Counter, Iterable]) -> int:
    """Count the shanten number of player's hand growing to Seven Pairs.

    The length of ``players_hand`` must be 13 or 14.

    Note that Seven Pairs must be of seven different pairs. Two identical pairs
    are not allowed.

    >>> count_shanten_seven_pairs(tiles.tiles('東東南南西西北北白白発発中中'))
    -1

    >>> count_shanten_seven_pairs('AABBCCDDEEFFG')
    0
    >>> count_shanten_seven_pairs('AABBCCDDEEFGH')
    1

    A hand with four different pairs is 2-shanten of Seven Pairs:

    >>> count_shanten_seven_pairs('AAABBBCCCDDEF')
    2
    >>> count_shanten_seven_pairs('AABBCCDDEFGHI')
    2

    >>> count_shanten_seven_pairs('AABBCCCCDEFGH')
    3
    >>> count_shanten_seven_pairs('ABCDEFabcdef0')
    6
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    if sum(player_hand.values()) not in (13, 14):
        raise ValueError('player_hand must be concealed')

    npair = sum(1 for v in player_hand.values() if v >= 2)
    #waiting_tiles = tuple(
    #    tile for tile in player_hand if player_hand[tile] < 2)

    return 6 - npair#, waiting_tiles


def count_shanten_naive(player_hand: Union[Counter, Iterable]) -> int:
    """Count the shanten number of player's hand.
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    return min(f(player_hand) for f in (
        count_shanten_std, count_shanten_seven_pairs, count_shanten_13_orphans))

if __name__ == '__main__':
    print(count_shanten_naive(tiles.tiles(sys.argv[1])))
