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

    def __init__(self, blacks, whites):
        random.seed()
        self.blacks = blacks
        self.whites = whites
        self.players = {}
        self.reset()

    def reset(self):
        self.white_stack = list(self.whites)
        self.black_stack = list(self.blacks)
        self.table = defaultdict(list)
        self.shuffled_table = list()
        self.current = None
        self.game_started = False
        self.current_czar = 0

    def start_game(self):
        self.reset()
        self.game_started = True
        for player in self.players.values():
            player.score = 0
        self.new_round()

    def add_player(self, name):
        player = Player(name)
        if self.game_started:
            if self.check_round_finished():
                # Pretend the new player has already played all cards so check_round_finished
                # doesn't return false on the initial state sent to the player
                player.cards_played = self.blanks()
            self.give_cards_to(player)
        self.players[name] = player

    def remove_player(self, name):
        if self.players[name].cardczar:
            del self.players[name]
            self.new_round()
        else:
            del self.players[name]
            del self.table[name]
            self.shuffle_table()

    def get_owner_of_cards(self, selected_cards):
        found = False
        for name, cards in self.table.items():
            if set(cards) == set(selected_cards):
                found = True
                break
        if not found:
            raise Exception('Selected cards don\'t exist!')
        return name

    def select_cards(self, selecting_player, selected_cards):
        if not self.players[selecting_player].cardczar:
            raise Exception('Must be Card Czar to select a card!')
        if not self.check_round_finished():
            raise Exception('Round has not yet finished!')
        name = self.get_owner_of_cards(selected_cards)
        self.players[name].score += 1
        self.new_round()
        return name

    def give_cards_to(self, player):
        if len(self.white_stack) < CARD_COUNT - len(player.hand):
            self.white_stack = list(self.whites)
        sample = random.sample(self.white_stack, CARD_COUNT - len(player.hand))
        for card in sample:
            self.white_stack.remove(card)
        player.hand += sample

    def give_cards(self):
        for player in self.players.values():
            self.give_cards_to(player)

    def shuffle_table(self):
        self.shuffled_table = list(self.table.values())
        random.shuffle(self.shuffled_table)

    def play_cards(self, playername, cards):
        player = self.players[playername]
        if player.cardczar:
            raise Exception('Card Czar can\'t play a card!')
        if player.cards_played + len(cards) > self.blanks():
            raise Exception('Tried to play too many cards!')
        for card in cards:
            if card not in player.hand:
                raise Exception('Can\'t play a card you don\'t have!')
            self.table[player.name].append(card)
            self.shuffle_table()
            player.cards_played += 1
            player.hand.remove(card)

    def check_round_finished(self):
        if not self.game_started:
            return False
        for player in self.players.values():
            if not player.cardczar and player.cards_played != self.blanks():
                return False
        return True

    def new_round(self):
        for player in self.players.values():
            player.cards_played = 0
            player.cardczar = False
        sorted_players = sorted(self.players.values(), key=lambda p1: p1.name)
        sorted_players[self.current_czar].cardczar = True
        self.current_czar = (self.current_czar + 1) % len(sorted_players)
        self.table.clear()
        self.give_cards()
        if len(self.black_stack) < 1:
            self.black_stack = list(self.blacks)
        self.current = random.sample(self.black_stack, 1)[0]
        self.black_stack.remove(self.current)

    def blanks(self):
        return max(self.current.count('_'), 1) if self.current else 0

    def get_player_state(self, playername):
        player = self.players[playername]
        round_finished = self.check_round_finished()
        cards_played = [l if name == playername else len(l) * ['']
                        for name, l in self.table.items()]
        return {
            'table': self.shuffled_table if round_finished else cards_played,
            'round_finished': round_finished,
            'hand': player.hand,
            'current': self.current,
            'blanks': self.blanks(),
            'game_started': self.game_started,
        }
