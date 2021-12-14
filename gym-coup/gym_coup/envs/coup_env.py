import gym
from random import shuffle


CARD_NAMES = ['Assassin',
              'Ambassador',
              'Captian',
              'Contessa',
              'Duke']

class Player:
    def __init__(self, id, is_human=False):
        self.id = id
        self.is_human = is_human
        self.cards = []
        self.is_card_face_up = [False, False]
        self.coins = 2

    def add_card(self, card):
        self.cards.append(card)

    def add_coins(self, num):
        self.coins += num

    def remove_coins(self, num):
        self.coins -= num

class Game:
    def __init__(self, num_human_players=0, num_cpu_players=2):
        self.players = [Player(i, True) for i in range(num_human_players)]
        self.players += [Player(i+num_human_players, False) for i in range(num_cpu_players)]

        if len(self.players) < 2 or len(self.players) > 6:
            print('Error: Game must have 2-6 players')
            return

        self.deck = [x * 3 for x in CARD_NAMES]
        self.shuffle_deck()
        self.deal_cards()

    def draw_card(self, index=0):
        return self.deck.pop(index)

    def shuffle_deck(self):
        self.deck = shuffle(self.deck)

    def deal_cards(self):
        for _ in range(2):
            for i in range(len(self.players)):
                self.players[i].add_card(self.draw_card())


class CoupEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, num_human_players=0, num_cpu_players=2):
        self.game = Game(num_human_players, num_cpu_players)

    def step(self, action):
        ...
    def reset(self):
        ...
    def render(self, mode='human'):
        ...
    def close(self):
        ...