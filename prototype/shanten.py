#!/usr/bin/env python

"""
mahjong.shanten
"""

from argparse import ArgumentParser, Namespace
from collections import Counter
from enum import Enum
from operator import itemgetter
import sys
from typing import Iterable, Sequence, Union

from melds import remove_melds, remove_pairs
import tiles

class ShantenType(Enum):
    """Types of player's hand"""

    STANDARD = '四面子一雀頭'
    THIRTEEN_ORPHANS = '国士無双'
    SEVEN_PAIRS = '七対子'


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

    >>> count_shanten_std(tiles.tiles('258m258p258s東南西北'))
    8
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    num_tile = sum(player_hand.values())
    if num_tile % 3 == 0:
        raise ValueError('the number of tiles must not be 3n.')

    if num_tile == 1:
        # Obvious tempai.
        return 0
    if num_tile == 2:
        if len(player_hand) == 1:
            # XX
            return -1
        # XY
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

    # 14, 13, 11, 10, 8, 7, 5, 4 -> 8, 8, 6, 6, 4, 4, 2, 2
    num_shanten = (num_tile - 1) // 3 * 2
    num_shanten -= sum(len(melds) for melds in (
        melds_m, melds_p, melds_s, melds_h)) * 2
    num_shanten -= min(4, sum(len(pairs) for pairs in (
        pairs_m, pairs_p, pairs_s, pairs_h)))

    return num_shanten


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
    # waiting_tiles = tuple(
    #    tile for tile in player_hand if player_hand[tile] < 2)

    return 6 - npair  # , waiting_tiles


def count_shanten_naive(player_hand: Union[Counter, Iterable]) -> int:
    """Count the shanten number of player's hand.
    """

    if not isinstance(player_hand, Counter):
        player_hand = Counter(player_hand)

    shanten, func = min(((f(player_hand), f) for f in (
        count_shanten_std,
        count_shanten_seven_pairs,
        count_shanten_13_orphans)),
        key=itemgetter(0))

    return shanten, func


def parse_args(args: Sequence[str]) -> Namespace:
    """Parse the command line parameters."

    Returns:
        An instance of argparse.ArgumentParser that stores the command line
        parameters.
    """

    parser = ArgumentParser()
    parser.add_argument(
        'hand',
        help='player\'s hand')
    parser.add_argument(
        '-a', '--algorithm',
        default=None,
        help='algorithm')

    return parser.parse_args(args or ['--help'])


def run(args):
    """main entry point"""

    player_hand = tiles.tiles(args.hand)

    func = {'13': count_shanten_13_orphans,
            '7': count_shanten_seven_pairs,
            'std': count_shanten_std, }.get(args.algorithm, None)

    if func:
        shanten = func(player_hand)
    else:
        shanten, func = count_shanten_naive(player_hand)

    shanten_type = {
        count_shanten_13_orphans: ShantenType.THIRTEEN_ORPHANS,
        count_shanten_seven_pairs: ShantenType.SEVEN_PAIRS,
        count_shanten_std: ShantenType.STANDARD }[func]

    print(f'{shanten} {shanten_type}')


def main(args=sys.argv[1:]):
    """main entry point"""
    sys.exit(run(parse_args(args)))


if __name__ == '__main__':
    main()
