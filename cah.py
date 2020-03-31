import random

from collections import defaultdict

CARD_COUNT = 6

class Player:

    def __init__(self, name):
        self.name = name
        self.hand = []
        self.cards_played = 0
        self.score = 0
        self.cardczar = False

class CAH:

    def __init__(self):
        self.blacks = []
        self.whites = []
        self.white_stack = []
        self.black_stack = []
        self.table = defaultdict(list)
        self.players = {}
        self.current = None

    def select_card(self, selecting_player, selected_player):
        if not self.players[selecting_player].cardczar:
            raise 'Must be Card Czar to select a card!'
        if not self.check_round_finished():
            raise 'Round has not yet finished!'
        self.players[selected_player].score += 1
        self.new_round()

    def give_cards(self):
        for player in self.players.values():
            if len(self.white_stack) < CARD_COUNT - len(player.hand):
                self.white_stack = list(self.whites)
            player.hand += random.sample(self.white_stack, CARD_COUNT - len(player.hand))
            for card in player.hand:
                self.white_stack.remove(card)

    def play_card(self, playername, *cards):
        player = self.players[playername]
        if player.cardczar:
            raise 'Card Czar can\'t play a card!'
        if player.cards_played + len(cards) > self.blanks():
            raise 'Tried to play too many cards!'
        for card in cards:
            self.table[player.name].append(player.hand[card])
            player.cards_played += 1
            del player.hand[card]

    def check_round_finished(self):
        for player in self.players.values():
            if not player.cardczar and player.cards_played != self.blanks():
                return False
        return True

    def new_round(self):
        for player in self.players.values():
            player.cards_played = 0
        self.give_cards()
        if len(self.black_stack) < 1:
            self.black_stack = list(self.blacks)
        self.current = random.sample(self.black_stack, 1)
        self.black_stack.remove(self.current)

    def blanks(self):
        return self.current.count('_')

    def get_player_state(self, playername):
        player = self.players[playername]
        round_finished = self.check_round_finished()
        cards_played = [l if name == playername else len(l) * [''] for name, l in self.table]
        return {
            'table': self.table.values() if round_finished else cards_played,
            'round_finished': self.check_round_finished(),
            'hand': player.hand,
            'current': self.current,
            'blanks': self.blanks()
        }
