"""
mahjong.tiles

"""

from collections import Counter
from itertools import chain, repeat
import re
import sys
from typing import Iterable, List, Tuple, Union
import unicodedata

# | コード | 牌画 | `unicodedata.name` |
# |-------:|------|:-------------------|
# | U+1F000 | 🀀 | MAHJONG TILE EAST WIND |
# | U+1F001 | 🀁 | MAHJONG TILE SOUTH WIND |
# | U+1F002 | 🀂 | MAHJONG TILE WEST WIND |
# | U+1F003 | 🀃 | MAHJONG TILE NORTH WIND |
# | U+1F004 | 🀄 | MAHJONG TILE RED DRAGON |
# | U+1F005 | 🀅 | MAHJONG TILE GREEN DRAGON |
# | U+1F006 | 🀆 | MAHJONG TILE WHITE DRAGON |
# | U+1F007 | 🀇 | MAHJONG TILE ONE OF CHARACTERS |
# | U+1F008 | 🀈 | MAHJONG TILE TWO OF CHARACTERS |
# | U+1F009 | 🀉 | MAHJONG TILE THREE OF CHARACTERS |
# | U+1F00A | 🀊 | MAHJONG TILE FOUR OF CHARACTERS |
# | U+1F00B | 🀋 | MAHJONG TILE FIVE OF CHARACTERS |
# | U+1F00C | 🀌 | MAHJONG TILE SIX OF CHARACTERS |
# | U+1F00D | 🀍 | MAHJONG TILE SEVEN OF CHARACTERS |
# | U+1F00E | 🀎 | MAHJONG TILE EIGHT OF CHARACTERS |
# | U+1F00F | 🀏 | MAHJONG TILE NINE OF CHARACTERS |
# | U+1F010 | 🀐 | MAHJONG TILE ONE OF BAMBOOS |
# | U+1F011 | 🀑 | MAHJONG TILE TWO OF BAMBOOS |
# | U+1F012 | 🀒 | MAHJONG TILE THREE OF BAMBOOS |
# | U+1F013 | 🀓 | MAHJONG TILE FOUR OF BAMBOOS |
# | U+1F014 | 🀔 | MAHJONG TILE FIVE OF BAMBOOS |
# | U+1F015 | 🀕 | MAHJONG TILE SIX OF BAMBOOS |
# | U+1F016 | 🀖 | MAHJONG TILE SEVEN OF BAMBOOS |
# | U+1F017 | 🀗 | MAHJONG TILE EIGHT OF BAMBOOS |
# | U+1F018 | 🀘 | MAHJONG TILE NINE OF BAMBOOS |
# | U+1F019 | 🀙 | MAHJONG TILE ONE OF CIRCLES |
# | U+1F01A | 🀚 | MAHJONG TILE TWO OF CIRCLES |
# | U+1F01B | 🀛 | MAHJONG TILE THREE OF CIRCLES |
# | U+1F01C | 🀜 | MAHJONG TILE FOUR OF CIRCLES |
# | U+1F01D | 🀝 | MAHJONG TILE FIVE OF CIRCLES |
# | U+1F01E | 🀞 | MAHJONG TILE SIX OF CIRCLES |
# | U+1F01F | 🀟 | MAHJONG TILE SEVEN OF CIRCLES |
# | U+1F020 | 🀠 | MAHJONG TILE EIGHT OF CIRCLES |
# | U+1F021 | 🀡 | MAHJONG TILE NINE OF CIRCLES |

# A range of code points
TILE_RANGE = range(0x1F000, 0x1F022)

# 風牌
TILE_RANGE_WINDS = range(0x1F000, 0x1F004)

# 三元牌
TILE_RANGE_DRAGONS = range(0x1F004, 0x1F007)

# 字牌
TILE_RANGE_HONORS = range(0x1F000, 0x1F007)

# 萬子
TILE_RANGE_CHARACTERS = range(0x1F007, 0x1F010)

# 筒子
TILE_RANGE_CIRCLES = range(0x1F019, 0x1F022)

# 索子
TILE_RANGE_BAMBOOS = range(0x1F010, 0x1F019)

# 数牌
TILE_RANGE_SUITS = range(0x1F007, 0x1F022)

# 么九牌
TILE_TERMINALS = (0x1F007, 0x1F00F, 0x1F019, 0x1F021, 0x1F010, 0x1F018)


def _define_instances():
    """Define all instances of the Mahjong tiles.

    >>> ns = globals()
    >>> import re
    >>> def _count_occurences(ns, pattern):
    ...     return sum(1 for i in ns.keys() if re.match(pattern, i))
    ...
    >>> _count_occurences(ns, r'TILE_.+_WIND$')
    4
    >>> _count_occurences(ns, r'TILE_.+_DRAGON$')
    3
    >>> _count_occurences(ns, r'TILE_(?!RANGE_).+_CHARACTERS$')
    9
    >>> _count_occurences(ns, r'TILE_(?!RANGE_).+_CIRCLES$')
    9
    >>> _count_occurences(ns, r'TILE_(?!RANGE_).+_BAMBOOS$')
    9
    """

    global_namespace = globals()
    for code in TILE_RANGE:
        # Convert "MAHJONG TILE XXXX YYYY" to "TILE_XXXX_YYYY"
        identifier = unicodedata.name(chr(code))[8:].replace(" ", "_")
        global_namespace[identifier] = code


_define_instances()


def get_name(*, tile_id=None, name=None) -> str:
    """Return unicodedata.name associated with ``tile``

    >>> get_name(tile_id=TILE_EAST_WIND)
    'MAHJONG TILE EAST WIND'

    >>> get_name(name='MAHJONG TILE EAST WIND')
    'MAHJONG TILE EAST WIND'
    """

    if tile_id:
        return unicodedata.name(chr(tile_id))

    if name:
        return name

    return None


def get_id(*, tile_id=None, name=None) -> int:
    """Return the ID of a tile.

    >>> tile = get_id(name='MAHJONG TILE EAST WIND')
    >>> tile == TILE_EAST_WIND
    True
    """

    if tile_id:
        return tile_id

    if name:
        return ord(unicodedata.lookup(name))

    return None


def is_honor(tile_id: int) -> bool:
    """Test if a tile is a Honor

    >>> all(is_honor(i) for i in TILE_RANGE_WINDS)
    True
    >>> all(is_honor(i) for i in TILE_RANGE_DRAGONS)
    True
    >>> any(is_honor(i) for i in TILE_RANGE_SUITS)
    False
    """

    return tile_id in TILE_RANGE_HONORS


def is_wind(tile_id: int) -> bool:
    """Test if a tile is a Wind

    >>> all(is_wind(i) for i in TILE_RANGE_WINDS)
    True
    >>> any(is_wind(i) for i in TILE_RANGE_DRAGONS)
    False
    >>> any(is_wind(i) for i in TILE_RANGE_SUITS)
    False
    """

    return tile_id in TILE_RANGE_WINDS


def is_dragon(tile_id: int) -> bool:
    """Test if a tile is a Dragon

    >>> any(is_dragon(i) for i in TILE_RANGE_WINDS)
    False
    >>> any(is_dragon(i) for i in TILE_RANGE_DRAGONS)
    True
    >>> any(is_dragon(i) for i in TILE_RANGE_SUITS)
    False
    """

    return tile_id in TILE_RANGE_DRAGONS


def is_suit(tile_id: int) -> bool:
    """Test if a tile is a Suit

    >>> any(is_suit(i) for i in TILE_RANGE_WINDS)
    False
    >>> any(is_suit(i) for i in TILE_RANGE_DRAGONS)
    False
    >>> all(is_suit(i) for i in TILE_RANGE_CHARACTERS)
    True
    >>> all(is_suit(i) for i in TILE_RANGE_CIRCLES)
    True
    >>> all(is_suit(i) for i in TILE_RANGE_BAMBOOS)
    True
    """

    return tile_id in TILE_RANGE_SUITS


def is_character(tile_id: int) -> bool:
    """Test if a tile is a Character

    >>> any(is_character(i) for i in TILE_RANGE_WINDS)
    False
    >>> any(is_character(i) for i in TILE_RANGE_DRAGONS)
    False
    >>> all(is_character(i) for i in TILE_RANGE_CHARACTERS)
    True
    >>> any(is_character(i) for i in TILE_RANGE_CIRCLES)
    False
    >>> any(is_character(i) for i in TILE_RANGE_BAMBOOS)
    False
    """

    return tile_id in TILE_RANGE_CHARACTERS


def is_circle(tile_id: int) -> bool:
    """Test if a tile is a Circle

    >>> any(is_circle(i) for i in TILE_RANGE_WINDS)
    False
    >>> any(is_circle(i) for i in TILE_RANGE_DRAGONS)
    False
    >>> any(is_circle(i) for i in TILE_RANGE_CHARACTERS)
    False
    >>> all(is_circle(i) for i in TILE_RANGE_CIRCLES)
    True
    >>> any(is_circle(i) for i in TILE_RANGE_BAMBOOS)
    False
    """

    return tile_id in TILE_RANGE_CIRCLES


def is_bamboo(tile_id: int) -> bool:
    """Test if a tile is a Bamboo

    >>> any(is_bamboo(i) for i in TILE_RANGE_WINDS)
    False
    >>> any(is_bamboo(i) for i in TILE_RANGE_DRAGONS)
    False
    >>> any(is_bamboo(i) for i in TILE_RANGE_CHARACTERS)
    False
    >>> any(is_bamboo(i) for i in TILE_RANGE_CIRCLES)
    False
    >>> all(is_bamboo(i) for i in TILE_RANGE_BAMBOOS)
    True
    """

    return tile_id in TILE_RANGE_BAMBOOS


def is_terminal(tile_id: int) -> bool:
    """Test is a tile is a Terminal, i.e. One or Nine.

    >>> [is_terminal(i) for i in TILE_RANGE_CHARACTERS]
    [True, False, False, False, False, False, False, False, True]
    """

    return tile_id in TILE_TERMINALS


def is_simple(tile_id: int) -> bool:
    """Test if a tile is not Terminal and not Honor

    >>> [is_simple(i) for i in TILE_RANGE_CHARACTERS]
    [False, True, True, True, True, True, True, True, False]
    """

    return is_suit(tile_id) and not is_terminal(tile_id)


def get_suit_number(tile_id: int) -> int:
    """Return the number of a given tile.

    >>> get_suit_number(TILE_ONE_OF_CHARACTERS)
    1
    >>> get_suit_number(TILE_TWO_OF_CIRCLES)
    2
    >>> get_suit_number(TILE_THREE_OF_BAMBOOS)
    3
    """

    if not is_suit(tile_id):
        raise ValueError(f'{tile_id} must be a Suit tile')

    return TILE_RANGE_SUITS.index(tile_id) % 9 + 1


# Filters
def _create_filter(tile_range):
    """A helper function."""
    return Counter(chain.from_iterable(repeat(tile_range, 4)))

FILTER_WINDS = _create_filter(TILE_RANGE_WINDS)
FILTER_DRAGONS = _create_filter(TILE_RANGE_DRAGONS)
FILTER_HONORS = FILTER_WINDS + FILTER_DRAGONS
FILTER_CHARACTERS = _create_filter(TILE_RANGE_CHARACTERS)
FILTER_CIRCLES = _create_filter(TILE_RANGE_CIRCLES)
FILTER_BAMBOOS = _create_filter(TILE_RANGE_BAMBOOS)
#FILTER_TERMINALS = _create_filter(TILE_TERMINALS)

_suit_baseid_table = {
    'm': TILE_ONE_OF_CHARACTERS,
    'p': TILE_ONE_OF_CIRCLES,
    's': TILE_ONE_OF_BAMBOOS,}

_honor_table = {
    '東': TILE_EAST_WIND,
    '南': TILE_SOUTH_WIND,
    '西': TILE_WEST_WIND,
    '北': TILE_NORTH_WIND,
    '白': TILE_WHITE_DRAGON,
    '発': TILE_GREEN_DRAGON,
    '中': TILE_RED_DRAGON,}


def tiles(pattern: str) -> Union[int, Tuple]:
    """Transform a string into tile instances.

    >>> tiles('5s') == TILE_FIVE_OF_BAMBOOS
    True
    >>> tiles('東') == TILE_EAST_WIND
    True

    >>> my_hand = Counter(tiles('3899m3457p88s南白発'))
    >>> my_hand[TILE_NINE_OF_CHARACTERS]
    2
    >>> my_hand[TILE_SOUTH_WIND]
    1
    """

    result = []
    regex = r'([1-9]+[mps])|([東南西北白発中]+)'

    for suits, honors in re.findall(regex, pattern):
        if suits:
            result.extend(_suit_baseid_table[suits[-1]] + int(i) - 1
                          for i in suits[:-1])
        else:
            result.extend(_honor_table[honor] for honor in honors)

    if len(result) <= 1:
        if not result:
            return ()
        return result[0]

    return tuple(result)


def list_tiles_md(file=sys.stdout):
    """List most Mahjong tiles in Markdown format"""

    # table header
    print('| コード | 牌画 | `unicodedata.name` |', file=file)
    print('|-------:|------|:-------------------|', file=file)

    for code in TILE_RANGE:
        char = chr(code)
        name = unicodedata.name(char)
        print(f'| U+{code:05X} | {char} | {name} |', file=file)


def _init_sortkey_map():
    """Return the mapping for sorting tiles"""

    sortkey_map = {}
    key = 1
    # マンピンソー東南西北白発中
    for code in chain(
            TILE_RANGE_CHARACTERS, TILE_RANGE_CIRCLES,
            TILE_RANGE_BAMBOOS, TILE_RANGE_WINDS,
            reversed(TILE_RANGE_DRAGONS)):
        sortkey_map[code] = key
        key += 1
    return sortkey_map


SORTKEY_MAP = _init_sortkey_map()


def sort_tiles(tilelist: List[int]):
    """Sort a list that contains tiles

    >>> SORTKEY_MAP[TILE_WHITE_DRAGON]
    32
    >>> SORTKEY_MAP[TILE_GREEN_DRAGON]
    33
    >>> SORTKEY_MAP[TILE_RED_DRAGON]
    34

    >>> L = [TILE_RED_DRAGON, TILE_ONE_OF_CIRCLES, TILE_EAST_WIND,
    ...      TILE_GREEN_DRAGON, TILE_ONE_OF_BAMBOOS, TILE_WHITE_DRAGON,
    ...      TILE_ONE_OF_CHARACTERS]
    >>> sort_tiles(L)
    >>> L == [TILE_ONE_OF_CHARACTERS, TILE_ONE_OF_CIRCLES, TILE_ONE_OF_BAMBOOS,
    ...       TILE_EAST_WIND, TILE_WHITE_DRAGON, TILE_GREEN_DRAGON,
    ...       TILE_RED_DRAGON]
    True
    """

    tilelist.sort(key=lambda t: SORTKEY_MAP[t])


TILE_SUCC_MAP = {
    TILE_NORTH_WIND: TILE_EAST_WIND,
    TILE_WHITE_DRAGON: TILE_GREEN_DRAGON,
    TILE_GREEN_DRAGON: TILE_RED_DRAGON,
    TILE_RED_DRAGON: TILE_WHITE_DRAGON,
    TILE_NINE_OF_CHARACTERS: TILE_ONE_OF_CHARACTERS,
    TILE_NINE_OF_BAMBOOS: TILE_ONE_OF_BAMBOOS,
    TILE_NINE_OF_CIRCLES: TILE_ONE_OF_CIRCLES,
}

TILE_PREC_MAP = {TILE_SUCC_MAP[_k]: _k for _k in TILE_SUCC_MAP}


def successor(tile_id: int) -> int:
    """Return the dora tile from dora indicator tile.

    If the dora indicator is a suit tile, the dora is the next tile in the
    same suit, e.g. seven bamboo is dora if six bamboo is the dora indicator.

    >>> assert successor(TILE_SIX_OF_BAMBOOS) == TILE_SEVEN_OF_BAMBOOS

    If the indicator is a nine, the dora is the one in the same suit.

    >>> assert successor(TILE_NINE_OF_CHARACTERS) == TILE_ONE_OF_CHARACTERS
    >>> assert successor(TILE_NINE_OF_CIRCLES) == TILE_ONE_OF_CIRCLES
    >>> assert successor(TILE_NINE_OF_BAMBOOS) == TILE_ONE_OF_BAMBOOS

    If the indicator is a dragon, the dora is also a dragon, and the following
    order applies: red points to white, white points to green and green points
    to red.

    >>> assert successor(TILE_WHITE_DRAGON) == TILE_GREEN_DRAGON
    >>> assert successor(TILE_GREEN_DRAGON) == TILE_RED_DRAGON
    >>> assert successor(TILE_RED_DRAGON) == TILE_WHITE_DRAGON

    For Winds, likewise, the following order applies:
    east-south-west-north-east.

    >>> assert successor(TILE_EAST_WIND) == TILE_SOUTH_WIND
    >>> assert successor(TILE_SOUTH_WIND) == TILE_WEST_WIND
    >>> assert successor(TILE_WEST_WIND) == TILE_NORTH_WIND
    >>> assert successor(TILE_NORTH_WIND) == TILE_EAST_WIND
    """

    return TILE_SUCC_MAP.get(tile_id, tile_id + 1)

# Suits

def convert_suit_to_number(player_hand: Union[Counter, Iterable]) -> Counter:
    """Convert a counter of tiles of a suit to of 0-9s.

    >>> convert_suit_to_number([])
    Counter()

    >>> characters = convert_suit_to_number(tiles('3899m'))
    >>> sorted(characters.elements())
    [3, 8, 9, 9]

    >>> circles = convert_suit_to_number(tiles('3457p'))
    >>> sorted(circles.elements())
    [3, 4, 5, 7]

    >>> bamboos = convert_suit_to_number(tiles('88s'))
    >>> sorted(bamboos.elements())
    [8, 8]

    >>> convert_suit_to_number(tiles('南南南'))
    Traceback (most recent call last):
        ...
    ValueError
    """

    if isinstance(player_hand, Counter):
        source = player_hand
    else:
        source = Counter(player_hand)

    if not source:
        return source

    tile_id = source.most_common(1)[0][0]
    if tile_id in TILE_RANGE_CHARACTERS:
        first = TILE_ONE_OF_CHARACTERS
    elif tile_id in TILE_RANGE_CIRCLES:
        first = TILE_ONE_OF_CIRCLES
    elif tile_id in TILE_RANGE_BAMBOOS:
        first = TILE_ONE_OF_BAMBOOS
    else:
        raise ValueError

    if all(first <= k <= first + 9 for k in source):
        return Counter({k - first + 1: source[k] for k in source})

    raise ValueError


# Melds and pairs

def _generate_all_melds_suit():
    """Generate 111, 123, 222, 234, 333, 345, ..., 777, 789, 888, 999.
    """

    for i in range(1, 10):
        yield Counter({i: 3})
        if i + 2 <= 9:
            yield Counter([i, i + 1, i + 2])


MELDS_NUMBER = tuple(_generate_all_melds_suit())
MELDS_HONOR = tuple(Counter({i: 3}) for i in TILE_RANGE_HONORS)


def _generate_all_pairs_suit():
    """TODO: optimize
    """

    for i in range(1, 10):
        yield Counter((i, i))
        if i < 9:
            yield Counter((i, i + 1))
        if i < 8:
            yield Counter((i, i + 2))

PAIRS_NUMBER = tuple(_generate_all_pairs_suit())
PAIRS_HONOR = tuple(Counter({i: 2}) for i in TILE_RANGE_HONORS)

THIRTEEN_ORPHANS = Counter(chain(TILE_TERMINALS, TILE_RANGE_HONORS))
