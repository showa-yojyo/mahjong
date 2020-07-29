"""
mahjong.player
"""

class Player:
    """A Mahjong player

    >>> player = Player('日蔭', 20000)
    >>> print(player)
    日蔭  20,000 点
    """

    def __init__(self, name, points=25000):
        self.name = name
        self.points = points # TODO: replace with score sticks
        self.seat_wind = None
        self.hand = None

    def __str__(self):
        contents = []
        if self.seat_wind:
            contents.append(f'{self.seat_wind!s}家')
        contents.append(f'{self.name}')
        contents.append(f'{self.points: 6,d} 点')
        if self.hand:
            contents.append(f'手牌 {self.hand:s}')
        return ' '.join(contents)
