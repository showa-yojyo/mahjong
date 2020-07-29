#!/usr/bin/env python

"""
mahjong.game
"""

import itertools
from operator import attrgetter
from random import shuffle

import dice
#import hand
#import startup
from player import Player
import tiles
import walls
from phase import Phase
from winds import (Winds, get_left_wind)


class Game:
    """Mahjong"""

    def __init__(self):
        self.players = None
        self.current_phase = None
        self.walls = None
        self.dead_wall_ends = None
        self.current_wall = None
        self.dice = None
        self.dora = None


    def __str__(self):
        return f'''{self.current_phase}
{self.players[0]}
{self.players[1]}
{self.players[2]}
{self.players[3]}
        '''


    def setup(self, player_names):
        """Setup the game"""

        self._setup_players(player_names)
        self._setup_seating_order()


    def _setup_players(self, player_names):
        """Entry"""

        self.players = [Player(name) for name in player_names]


    def _setup_seating_order(self, seed_func=None):
        """Decide the seating order and dealer.

        random: This argument is passed to random.shuffle().
        """

        seating_order = list(Winds)
        shuffle(seating_order, seed_func)

        for player, wind in zip(self.players, seating_order):
            player.prevalent_wind = wind
        self._update_players()


    def _setup_hand(self, prevalent_wind, new_hand):
        """Initialize a hand"""

        self.current_phase = Phase(prevalent_wind, new_hand, 0)


    def rebuild_walls(self):
        """Build the walls on the table"""

        duplicate = len(self.players)
        all_tiles = [chr(i) for i in tiles.TILE_RANGE] * duplicate
        shuffle(all_tiles)
        self.walls = walls.build_walls(all_tiles, duplicate)


    def break_walls(self):
        """Determine which position to break the walls

        <East rolls two dice and counts that number of players
        counter-clockwise, starting with himself. The player thus
        determined breaks the wall in front of him, by counting
        from the right the same number of stacks as indicated by
        the dice.> (Rules for Japanese Mahjong, 2016)
        """

        self.dice = dice.toss(2)
        nsum = sum(self.dice)
        wind = Winds((nsum - 1) % 4)
        print(f'サイコロ {self.dice} 割れ目 {wind!s}家 右から {nsum} トン目で割る')

        self.dead_wall_ends = walls.dead_wall_ends(wind, nsum)

        return (wind, nsum)


    def deal_tiles(self, wind, nsum):
        """Deal 13 tiles to each player

        The first 4 tiles will be taken from:
            nsum=1 -> walls[EAST][-3:-7:-1], where -3 == -2 - 1.
            nsum=2 -> walls[SOUTH][-5:-9:-1], where -5 == -4 - 1.
            nsum=3 -> walls[WEST][-7:-11:-1], where -7 == -6 - 1.
        """

        #print('配牌...')
        assert int(wind) == (nsum - 1) % 4

        self.current_wall = self.walls[wind]
        self.current_wall.curpos = -(2 * nsum) - 1

        # Deal 4 * 3 tiles for each player
        for _ in range(3):
            for player in self.players:
                tile_block = self.current_wall.deal_tiles()

                if (nblock := len(tile_block)) <= 2:
                    assert nblock in (0, 2)

                    # Change the wall and take two tiles
                    wind = get_left_wind(wind)
                    self.current_wall = self.walls[wind]
                    tile_block.extend(self.current_wall.deal_tiles(4 - nblock))

                assert len(tile_block) == 4
                player.hand.extend(tile_block)

        assert all(len(p.hand) == 12 for p in self.players)

        # Take 13th tile
        for player in self.players:
            if not (tile := self.current_wall.draw_tile()):
                wind = get_left_wind(wind)
                self.current_wall = self.walls[wind]
                tile = self.current_wall.draw_tile()
            player.hand.append(tile)
            player.print_hand()

        assert all(len(p.hand) == 13 for p in self.players)
        self.print_walls()


    def print_walls(self):
        """Debug write the walls"""

        for wind, wall in enumerate(self.walls):
            print(f'牌山 {Winds(wind)!s}')
            print(wall)


    def reset_dora(self):
        """Determine the dora indicator and turn it over"""

        dora_indicator_index = self.dead_wall_ends[0].index + 5
        if dora_indicator_index < 34:
            wind = self.dead_wall_ends[0].wind
        else:
            wind = self.dead_wall_ends[1].wind
            dora_indicator_index %= 34

        #print(f'ドラ表示牌 {wind = } {dora_indicator_index = }')
        self.dora = tiles.successor(self.walls[wind][dora_indicator_index])
        print(f'ドラ {tiles.get_name(self.dora)}')


    def run(self):
        """Main loop of a Mahjong game"""

        for prevalent_wind in (Winds.EAST, Winds.SOUTH):
            for cur_hand in range(1, 5):
                for stick in itertools.count(0):
                    phase = Phase(prevalent_wind, cur_hand, stick)
                    print(phase)
                    self.current_phase = phase
                    if stick:
                        self.update_seat_winds(phase)
                    self.rebuild_walls()
                    seat_wind, nsum = self.break_walls()
                    self.deal_tiles(seat_wind, nsum)
                    self.reset_dora()
                    keep_dealership = hand.run()
                    self.cleanup_phase()
                    if not keep_dealership:
                        break


    def cleanup_phase(self):
        """Clean up e.g. 東一局一本場"""

        for p in self.players:
            p.hand.clear()

        self.walls = None
        self.dead_wall_ends = None
        self.current_wall = None
        self.dice = None
        self.dora = None


    def update_seat_winds(self, phase):
        """Rotate seat winds if needed, i.e. S, W, N, E = E, S, W, N.
        """

        if phase.counter > 0 or (
                phase.prevalent_wind == Winds.EAST and phase.hand == 1):
            return False

        for player in self.players:
            player.seat_wind = get_left_wind(player.seat_wind)

        self._update_players()
        return True


    def _update_players(self):
        self.players.sort(key=attrgetter('prevalent_wind'))


def main():
    """main entry point"""

    # TODO: matchmaking
    player_names = ('後堂', '橋場', '山下', '日蔭')

    game = Game()
    game.setup(player_names)
    print(game)
    #game.run()


if __name__ == "__main__":
    main()
