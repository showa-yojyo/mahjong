"""
mahjong.payment
"""

from enum import Enum
from typing import Tuple, Union

class LimitHand(Enum):
    """Enumeration of limit hands"""

    MANGAN = '満貫'
    HANEMAN = '跳満'
    BAIMAN = '倍満'
    SANBAIMAN = '三倍満'
    YAKUMAN = '役満'

PAYMENT_TABLE_DEALER_TSUMO = {
    20: (0, 0, 700, 1300, 2600),
    25: (0, 0, 0, 1600, 3200),
    30: (0, 500, 1000, 2000, 3900),
    40: (0, 700, 1300, 2600, 4000),
    50: (0, 800, 1600, 3200, 4000),
    60: (0, 1000, 2000, 3900, 4000),
    70: (0, 1200, 2300, 4000, 4000),
    80: (0, 1300, 2600, 4000, 4000),
    90: (0, 1500, 2900, 4000, 4000),
    100: (0, 1600, 3200, 4000, 4000),
}

PAYMENT_TABLE_DEALER_RON = {
    25: (0, 0, 2400, 4800, 9600),
    30: (0, 1500, 2900, 5800, 11600),
    40: (0, 2000, 3900, 7700, 12000),
    50: (0, 2400, 4800, 9600, 12000),
    60: (0, 2900, 5800, 11600, 12000),
    70: (0, 3400, 6800, 12000, 12000),
    80: (0, 3900, 7700, 12000, 12000),
    90: (0, 4400, 8700, 12000, 12000),
    100: (0, 4800, 9600, 12000, 12000),
}

PAYMENT_TABLE_NON_DEALER_TSUMO = {
    20: ((0, 0), (0, 0), (400, 700), (700, 1300), (1300, 2600)),
    25: ((0, 0), (0, 0), (0, 0), (800, 1600), (1600, 3200)),
    30: ((0, 0), (300, 500), (500, 1000), (1000, 2000), (2000, 3900)),
    40: ((0, 0), (400, 700), (700, 1300), (1300, 2600), (2000, 4000)),
    50: ((0, 0), (400, 800), (800, 1600), (1600, 3200), (2000, 4000)),
    60: ((0, 0), (500, 1000), (1000, 2000), (2000, 3900), (2000, 4000)),
    70: ((0, 0), (600, 1200), (1200, 2300), (2000, 4000), (2000, 4000)),
    80: ((0, 0), (700, 1300), (1300, 2600), (2000, 4000), (2000, 4000)),
    90: ((0, 0), (800, 1500), (1500, 2900), (2000, 4000), (2000, 4000)),
    100: ((0, 0), (800, 1600), (1600, 3200), (2000, 4000), (2000, 4000)),
}

PAYMENT_TABLE_NON_DEALER_RON = {
    25: (0, 0, 1600, 3200, 6400),
    30: (0, 1000, 2000, 3900, 7700),
    40: (0, 1300, 2600, 5200, 8000),
    50: (0, 1600, 3200, 6400, 8000),
    60: (0, 2000, 3900, 7700, 8000),
    70: (0, 2300, 4500, 8000, 8000),
    80: (0, 2600, 5200, 8000, 8000),
    90: (0, 2900, 5800, 8000, 8000),
    100: (0, 3200, 6400, 8000, 8000),
}


def get_payment(
        minipoints: int,
        fan: int, winner_is_dealer: bool,
        on_self_draw: bool) -> Union[int, Tuple[int, int]]:
    """Return the payment

    >>> get_payment(30, 1, False, False)
    1000
    >>> get_payment(30, 1, False, True)
    (300, 500)
    >>> get_payment(30, 1, True, False)
    1500
    >>> get_payment(30, 1, True, True)
    500

    Note that rounded-up-Mangan is applied:

    >>> get_payment(30, 4, False, True)
    (2000, 4000)
    >>> get_payment(30, 4, True, True)
    4000
    >>> get_payment(60, 3, False, True)
    (2000, 4000)
    >>> get_payment(60, 3, True, True)
    4000
    """

    if fan >= 5:
        return get_payment_limit_hands(
            get_limit_hand(fan), winner_is_dealer, on_self_draw)

    if (minipoints, fan) in ((30, 4), (60, 3)):
        return get_payment_limit_hands(
            LimitHand.MANGAN, winner_is_dealer, on_self_draw)

    if winner_is_dealer:
        if on_self_draw:
            table = PAYMENT_TABLE_DEALER_TSUMO
        else:
            table = PAYMENT_TABLE_DEALER_RON
    else:
        if on_self_draw:
            table = PAYMENT_TABLE_NON_DEALER_TSUMO
        else:
            table = PAYMENT_TABLE_NON_DEALER_RON

    return table[minipoints][fan]


PAYMENT_TABLE_DEALER_LIMIT_HAND = {
    LimitHand.MANGAN: 4000,
    LimitHand.HANEMAN: 6000,
    LimitHand.BAIMAN: 8000,
    LimitHand.SANBAIMAN: 12000,
    LimitHand.YAKUMAN: 16000,
}

PAYMENT_TABLE_NON_DEALER_LIMIT_HAND = {
    LimitHand.MANGAN: (2000, 4000),
    LimitHand.HANEMAN: (3000, 6000),
    LimitHand.BAIMAN: (4000, 8000),
    LimitHand.SANBAIMAN: (6000, 12000),
    LimitHand.YAKUMAN: (8000, 16000),
}

def get_limit_hand(fan: int) -> LimitHand:
    """Return the name of limit hand corresponding to the fan value.

    >>> for i in range(5, 14):
    ...     print(get_limit_hand(i).value)
    満貫
    跳満
    跳満
    倍満
    倍満
    倍満
    三倍満
    三倍満
    役満
    """

    if fan == 5:
        return LimitHand.MANGAN
    if fan in (6, 7):
        return LimitHand.HANEMAN
    if fan in (8, 9, 10):
        return LimitHand.BAIMAN
    if fan in (11, 12):
        return LimitHand.SANBAIMAN
    if fan >= 13:
        return LimitHand.YAKUMAN

    raise KeyError


def get_payment_limit_hands(
        key: LimitHand,
        winner_is_dealer: bool,
        on_self_draw: bool) -> Union[int, Tuple[int, int]]:
    """Return the payment for hands worth five or more fan.

    >>> get_payment_limit_hands(LimitHand.MANGAN, False, False)
    8000
    >>> get_payment_limit_hands(LimitHand.MANGAN, False, True)
    (2000, 4000)
    >>> get_payment_limit_hands(LimitHand.MANGAN, True, False)
    12000
    >>> get_payment_limit_hands(LimitHand.MANGAN, True, True)
    4000
    """

    if winner_is_dealer:
        table = PAYMENT_TABLE_DEALER_LIMIT_HAND
    else:
        table = PAYMENT_TABLE_NON_DEALER_LIMIT_HAND

    payment = table[key]
    if not on_self_draw:
        if winner_is_dealer:
            payment *= 3
        else:
            payment = payment[0] * 4

    return payment
