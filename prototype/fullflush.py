"""
How many are there concealed hands entirely of tiles from only one of the three
suits?
"""

from collections import Counter
from functools import lru_cache
from itertools import product
#from math import comb, perm
import sys

DUPLICATE = 4

@lru_cache(maxsize=7)
def count_menchin_cases(num):
    r"""Count the number of combinations :math:`(n_1, \dotsc, n_9)`, where
    :math:`\sum n_i = 13` and :math:`n_i \le 4`.

    >>> count_menchin_cases(0)
    [Counter({1: 1})]
    >>> count_menchin_cases(1)
    [Counter({1: 1})]
    >>> count_menchin_cases(2)
    [Counter({1: 2}), Counter({2: 1})]
    >>> count_menchin_cases(3)
    [Counter({1: 3}), Counter({1: 1, 2: 1}), Counter({3: 1})]
    """

    if num in (0, 1):
        return [Counter({1: 1}),]
    if num == 2:
        return [Counter({1: 2}), Counter({2: 1})]

    results = []
    last = num // 2 + 1
    for i in range(1, last):
        for lhs, rhs in product(count_menchin_cases(i), count_menchin_cases(num - i)):
            union = lhs + rhs
            if union in results:
                continue

            # Remove one that contains identical tiles more than four.
            if any(k > DUPLICATE for k in union):
                continue
            # Remove one that contains different tiles more than nine.
            if sum(union.values()) > 9:
                continue

            results.append(union)

    if num <= DUPLICATE:
        results.append(Counter({num: 1}))

    return results

if __name__ == '__main__':
    ntile = int(sys.argv[1])

    cases = count_menchin_cases(ntile)
    print(f'num of cases: {len(cases)}')
    for case in cases:
        ntype = sum(case.values())
        print(f'{repr(case)}')
