#!/usr/bin/env python

"""
mahjong.game
"""

from enum import Enum
from operator import attrgetter
from random import shuffle

import dice
from player import Player
from playerhand import PlayerHand
import tiles
from walls import TileWallAgent
from phase import Phase
from winds import (Winds, get_left_wind)


class GameType(Enum):
    """Type of Mahjong game"""

    EAST_ROUND_ONLY = '東風戦'
    EAST_AND_SOUTH_ROUNDS = '半荘戦'


class Game:
    """Mahjong"""

    def __init__(self, game_type: GameType):
        self.game_type = game_type
        self.players = None
        self.current_phase = None
        self.wall_agent = TileWallAgent()

    def __str__(self):
        output = [f'{self.game_type.value}']
        if self.current_phase:
            output.append(f'{self.current_phase}')
        else:
            output.append('(Out of the game)')

        output.extend(f'{player}' for player in self.players)
        return '\n'.join(output)

    def setup(self, player_names):
        """Setup the game"""

        self._setup_players(player_names)
        self._setup_seating_order()


    def _setup_players(self, player_names):
        """Entry"""

        if self.game_type == GameType.EAST_ROUND_ONLY:
            origin_points = 20000
        else:
            origin_points = 25000

        self.players = [Player(name, origin_points) for name in player_names]


    def _setup_seating_order(self, seed_func=None):
        """Decide the seating order and dealer.

        random: This argument is passed to random.shuffle().
        """

        seating_order = list(Winds)
        shuffle(seating_order, seed_func)

        for player, wind in zip(self.players, seating_order):
            player.seat_wind = wind
        self._update_players()


    def _setup_hand(self, prevalent_wind, new_hand):
        """Initialize a hand"""

        self.current_phase = Phase(prevalent_wind, new_hand, 0)


    def rebuild_walls(self):
        """Build the walls on the table"""

        return self.wall_agent.build()


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

    def run(self):
        """Main loop of a Mahjong game"""

        phase = Phase(Winds.EAST, 1, 0)
        self.current_phase = phase

        while True:
            player_hands = self.rebuild_walls()
            for player, hand in zip(self.players, player_hands):
                player.hand = PlayerHand(hand)

            # TODO: something interaction

            update_dealer, increment_counter = True, False
            self.on_finished_hand()
            self.cleanup_phase()
            if self.is_finished(update_dealer):
                break

            phase.proceed(update_dealer, increment_counter)
            self.rotate_seat_winds(phase)

    def is_finished(self, update_dealer: bool) -> bool:
        """Test if the game is over."""

        # Does some player's score goes below zero?
        if any(p.points < 0 for p in self.players):
            return True

        if self.current_phase.hand < 4:
            return False

        if not update_dealer:
            return True

        # アガリやめ
        gtype, pwind = self.game_type, self.current_phase.prevalent_wind
        if ((gtype == GameType.EAST_ROUND_ONLY
             and pwind == Winds.EAST) or (
                 gtype == GameType.EAST_AND_SOUTH_ROUNDS
                 and pwind == Winds.SOUTH)):

            top = max(self.players, key=attrgetter('points'))
            if top == self.players[0]:
                return True

        return False


    def cleanup_phase(self):
        """Clean up e.g. 東一局一本場"""

        for player in self.players:
            player.hand = None


    def rotate_seat_winds(self, phase):
        """Rotate seat winds if needed, i.e. S, W, N, E = E, S, W, N.
        """

        if phase.counter > 0:
            return False

        for player in self.players:
            player.seat_wind = get_left_wind(player.seat_wind)

        self._update_players()
        return True


    def _update_players(self):
        self.players.sort(key=attrgetter('seat_wind'))

    def on_finished_hand(self):
        #print(self)
        pass


def main():
    """main entry point"""

    # TODO: matchmaking
    player_names = ('後堂', '橋場', '山下', '日蔭')

    # TODO: regulation
    game = Game(GameType.EAST_ROUND_ONLY)
    game.setup(player_names)
    game.run()


if __name__ == "__main__":
    main()
