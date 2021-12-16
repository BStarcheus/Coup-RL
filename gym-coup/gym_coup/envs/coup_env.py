import gym
import numpy as np
from random import shuffle

# Cards
CARD_NAMES = ['Assassin',
              'Ambassador',
              'Captian',
              'Contessa',
              'Duke']
ASSASSIN   = 0
AMBASSADOR = 1
CAPTAIN    = 2
CONTESSA   = 3
DUKE       = 4

# Actions
INCOME             = 0
FOREIGN_AID        = 1
COUP               = 2
TAX                = 3
ASSASSINATE        = 4
EXCHANGE           = 5
EXCHANGE_RETURN_12 = 6
EXCHANGE_RETURN_13 = 7
EXCHANGE_RETURN_14 = 8
EXCHANGE_RETURN_23 = 9
EXCHANGE_RETURN_24 = 10
EXCHANGE_RETURN_34 = 11
STEAL              = 12
BLOCK              = 13
CHALLENGE          = 14
LOSE_CARD_1        = 15
LOSE_CARD_2        = 16
PASS_              = 17

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

        self.deck = 3 * [i for i in range(len(CARD_NAMES))]
        self.shuffle_deck()
        self.deal_cards()

        # P1 = 0, P2 = 1
        # Whose overall turn is it?
        self.whose_turn = 0
        # Turns can include several sub-actions.
        # Who is currently choosing an action?
        self.whose_action = 0

        self.turn_count = 0

    def print_player(self, p_ind):
        p = self.players[p_ind]
        print(f'P{p_ind + 1}:', CARD_NAMES[p.cards[0]], '|', p.is_card_face_up[0], '|',
                                CARD_NAMES[p.cards[1]], '|', p.is_card_face_up[1], '|',
              p.coins, '|', '_' if p.last_action == None else CoupEnv.actions[p.last_action])

    def render(self):
        print('Turn', self.turn_count)
        print('Player: Card1 | FaceUp | Card2 | FaceUp | Coins | LastAction')
        self.print_player(0)
        self.print_player(1)

    def draw_card(self, index=0):
        return self.deck.pop(index)

    def shuffle_deck(self):
        shuffle(self.deck)

    def deal_cards(self):
        for _ in range(2):
            for p in self.players:
                p.add_card(self.draw_card())

    def next_player_turn(self):
        '''
        Increment whose turn it is
        Turns can include several sub-actions
            ex: P1 Steal, P2 Block, P1 Challenge
                is a single turn of 3 actions
        '''
        self.whose_turn = 1 - self.whose_turn
        self.turn_count += 1

    def next_player_action(self):
        '''
        Increment whose action it is
        '''
        self.whose_action = 1 - self.whose_action

    def get_curr_action_player(self):
        return self.players[self.whose_action]

    def get_opp_player(self):
        return self.players[1 - self.whose_action]

    def get_valid_actions(self):
        curr_player = self.get_curr_action_player()
        opp_player = self.get_opp_player()

        if self.whose_turn != self.whose_action:
            # It is opp_player's turn, and curr_player can
            # choose to block or challenge for certain actions

            if opp_player.last_action == FOREIGN_AID:
                return [PASS_, BLOCK]
            elif opp_player.last_action in [TAX, EXCHANGE]:
                return [PASS_, CHALLENGE]
            elif opp_player.last_action == STEAL:
                return [PASS_, BLOCK, CHALLENGE]
            elif opp_player.last_action in [ASSASSINATE, COUP, CHALLENGE]:
                # CHALLENGE will only reach here if the opp_player challenges a block,
                # and the challenge succeeds (curr_player must lose a card)

                ret = []
                for i in range(2):
                    if not curr_player.is_card_face_up[i]:
                        # Card is still in play. Can choose to give it up.
                        ret += [LOSE_CARD_1 + i]

                if opp_player.last_action == ASSASSINATE:
                    ret += [BLOCK, CHALLENGE]

                return ret
            else:
                print("Error: invalid action progression")
                return

        elif opp_player.last_action == BLOCK:
            # It is curr_player's turn and opp_player wants to block their move
            return [PASS_, CHALLENGE]

        else:
            # It's the beginning of curr_player's turn

            if curr_player.coins >= 10:
                return [COUP]

            ret = [INCOME, FOREIGN_AID, TAX, EXCHANGE]
            if curr_player.coins >= 3:
                ret.append(ASSASSINATE)
            if curr_player.coins >= 7:
                ret.append(COUP)
            if opp_player.coins > 0:
                ret.append(STEAL)

            return ret


    def income(self):
        curr_player = self.get_curr_action_player()
        curr_player.add_coins(1)
        curr_player.last_action = INCOME
        self.next_player_action()
        self.next_player_turn()

    def foreign_aid(self):
        ...

    def coup(self):
        curr_player = self.get_curr_action_player()
        if curr_player.coins < 7:
            print('Error: not possible to coup with < 7 coins')
            return

        curr_player.remove_coins(7)
        curr_player.last_action = COUP
        self.next_player_action()

    def tax(self):
        ...

    def assassinate(self):
        ...

    def exchange(self):
        ...

    def exchange_return_12(self):
        ...

    def exchange_return_13(self):
        ...

    def exchange_return_14(self):
        ...

    def exchange_return_23(self):
        ...

    def exchange_return_24(self):
        ...

    def exchange_return_34(self):
        ...

    def steal(self):
        ...

    def block(self):
        ...

    def challenge(self):
        ...

    def _lose_card(self, card):
        curr_player = self.get_curr_action_player()
        if curr_player.is_card_face_up[card]:
            print('Error: cannot lose a card that is already face up')
            return

        curr_player.is_card_face_up[card] = True
        curr_player.last_action = LOSE_CARD_1 + card
        self.next_player_turn()
        # Lose card will always be the last action of a turn
        # so the next action is the start of the next player's turn
        self.whose_action = self.whose_turn

    def lose_card_1(self):
        self._lose_card(0)

    def lose_card_2(self):
        self._lose_card(1)

    def pass_(self):
        ...



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
        17: 'pass_'         # only an option when asked whether you'd
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
        #     Whose next action  (0, 1)
        # Note: some observations will never occur in game
        #       ex: All 4 cards are the same. Both players have all cards face up.
        low  = np.zeros(9, dtype='uint8')
        high = np.array([14, 14, 3,  3,  12, 12, len(self.actions), len(self.actions), 1], dtype='uint8')
        self.observation_space = gym.spaces.Box(low, high, dtype='uint8')

    def step(self, action):
        getattr(self.game, self.actions[action])()
    
    def reset(self):
        self.game = Game(self.num_human_players)

    def render(self, mode='human'):
        self.game.render()
    
    def close(self):
        ...
