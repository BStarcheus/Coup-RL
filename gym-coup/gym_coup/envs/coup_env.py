import gym
import numpy as np
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
        self.last_action = None

    def add_card(self, card):
        self.cards.append(card)

    def add_coins(self, num):
        self.coins += num

    def remove_coins(self, num):
        self.coins -= num

class Game:
    '''
    2 player Coup game
    Can have any combination of human and cpu players
    '''
    def __init__(self, num_human_players=0):
        self.players = [Player(i, True) for i in range(num_human_players)]
        self.players += [Player(i+num_human_players, False) for i in range(2-num_human_players)]

        self.deck = 3 * CARD_NAMES
        self.shuffle_deck()
        self.deal_cards()

        # P1 = 0, P2 = 1
        self.whose_turn = 0

    def draw_card(self, index=0):
        return self.deck.pop(index)

    def shuffle_deck(self):
        shuffle(self.deck)

    def deal_cards(self):
        for _ in range(2):
            for p in self.players:
                p.add_card(self.draw_card())


class CoupEnv(gym.Env):
    '''
    Gym env wrapper for a 2p Coup game
    '''
    metadata = {'render.modes': ['human']}

    actions = {
        0:  'income',
        1:  'foreign_aid',
        2:  'coup',
        3:  'tax',
        4:  'assassinate',
        5:  'exchange', # pick up 2 cards from court deck
        6:  'exchange_return_12', # return cards 1,2 to court deck
        7:  'exchange_return_13', # return cards 1,3
        8:  'exchange_return_14', # return cards 1,4
        9:  'exchange_return_23', # return cards 2,3
        10: 'exchange_return_24', # return cards 2,4
        11: 'exchange_return_34', # return cards 3,4
        12: 'steal',
        13: 'block',       # block the opponent's move
        14: 'challenge',   # challenge the opponent's move
        15: 'lose_card_1', # choose which card to lose
        16: 'lose_card_2',
        17: 'pass'         # only an option when asked whether you'd
                           # like to block or challenge your opponent's last move
    }

    def __init__(self, num_human_players=0):
        self.num_human_players = num_human_players
        self.game = Game(num_human_players)

        self.action_space = gym.spaces.Discrete(len(self.actions))

        # Observation:
        #     P1 card config     (0 - 14) unique (alph sorted) hands for 1 player
        #     P2 card config     (0 - 14)
        #     P1 is card face up (0 - 3) each cmb of 2 cards face up and down
        #     P2 is card face up (0 - 3)
        #     P1 # coins         (0 - 12)
        #     P2 # coins         (0 - 12)
        #     P1 last action
        #     P2 last action
        #     Whose turn         (0, 1)
        # Note: some observations will never occur in game
        #       ex: All 4 cards are the same. Both players have all cards face up.
        low  = np.zeros(9, dtype='uint8')
        high = np.array([14, 14, 3,  3,  12, 12, len(self.actions), len(self.actions), 1], dtype='uint8')
        self.observation_space = gym.spaces.Box(low, high, dtype='uint8')

    def step(self, action):
        ...
    
    def reset(self):
        self.game = Game(self.num_human_players)

    def render(self, mode='human'):
        ...
    
    def close(self):
        ...
