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
PASS_              = 13
BLOCK              = 14
CHALLENGE          = 15
LOSE_CARD_1        = 16
LOSE_CARD_2        = 17


class Player:
    def __init__(self, id, is_human=False):
        self.id = id
        self.is_human = is_human
        self.cards = []
        self.is_card_face_up = [False, False]
        self.coins = 2
        self.last_action = None

        # Indicate that the player has lost a challenge
        # and must choose which card to lose
        self.lost_challenge = False

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

        # Is it the beginning of a new turn?
        self.is_turn_begin = True

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
        # Players will always have the first action on their turn
        self.whose_action = self.whose_turn
        self.turn_count += 1
        self.is_turn_begin = True

    def next_player_action(self):
        '''
        Increment whose action it is
        '''
        self.whose_action = 1 - self.whose_action
        self.is_turn_begin = False

    def get_curr_action_player(self):
        return self.players[self.whose_action]

    def get_opp_player(self):
        return self.players[1 - self.whose_action]

    def get_valid_actions(self):
        curr_player = self.get_curr_action_player()
        opp_player = self.get_opp_player()

        def valid_lose_card_options():
            valid = []
            if not curr_player.is_card_face_up[0]:
                # Card is still in play. Can choose to give it up.
                valid += [LOSE_CARD_1]
            if not curr_player.is_card_face_up[1]:
                # Card is still in play. Can choose to give it up.
                valid += [LOSE_CARD_2]
            return valid


        if self.is_turn_begin:
            # It's the beginning of curr_player's turn

            if curr_player.coins >= 10:
                return [COUP]

            valid = [INCOME, FOREIGN_AID, TAX, EXCHANGE]
            if curr_player.coins >= 3:
                valid.append(ASSASSINATE)
            if curr_player.coins >= 7:
                valid.append(COUP)
            if opp_player.coins > 0:
                valid.append(STEAL)
            
            return valid

        elif curr_player.lost_challenge:
            return valid_lose_card_options()

        elif self.whose_turn != self.whose_action:
            # It is opp_player's turn, and curr_player can
            # choose to block or challenge for certain actions

            if opp_player.last_action == FOREIGN_AID:
                return [PASS_, BLOCK]
            elif opp_player.last_action in [TAX, EXCHANGE]:
                return [PASS_, CHALLENGE]
            elif opp_player.last_action == STEAL:
                return [PASS_, BLOCK, CHALLENGE]
            elif opp_player.last_action in [ASSASSINATE, COUP]:
                valid = valid_lose_card_options()

                if opp_player.last_action == ASSASSINATE:
                    valid += [BLOCK, CHALLENGE]

                return valid
            else:
                print('Error: invalid action progression')
                return

        elif curr_player.last_action == EXCHANGE:
            # It is curr_player's turn, and opp_player has approved the exchange

            if len(curr_player.cards) < 4:
                print('Error: player mid-exchange should have 4 cards including any eliminated')
                return
            
            valid = [EXCHANGE_RETURN_34]
            if not curr_player.is_card_face_up[0]:
                valid += [EXCHANGE_RETURN_13, EXCHANGE_RETURN_14]
            if not curr_player.is_card_face_up[1]:
                valid += [EXCHANGE_RETURN_23, EXCHANGE_RETURN_24]
            if (not curr_player.is_card_face_up[0] and
                not curr_player.is_card_face_up[1]):
                valid += [EXCHANGE_RETURN_12]

            return valid

        elif opp_player.last_action == BLOCK:
            # It is curr_player's turn and opp_player wants to block their move
            return [PASS_, CHALLENGE]
        
        else:
            print('Error: invalid action progression')


    def income(self):
        curr_player = self.get_curr_action_player()
        curr_player.add_coins(1)
        curr_player.last_action = INCOME
        self.next_player_turn()

    def foreign_aid(self):
        if self.is_turn_begin:
            # Before allowing the action to take effect, the opponent must not block it
            self.get_curr_action_player().last_action = FOREIGN_AID
            self.next_player_action()
        else:
            # PASS: Opponent did not block, so complete the action
            self.get_curr_action_player().add_coins(2)
            self.next_player_turn()

    def coup(self):
        curr_player = self.get_curr_action_player()
        if curr_player.coins < 7:
            print('Error: not possible to coup with < 7 coins')
            return

        curr_player.remove_coins(7)
        curr_player.last_action = COUP
        self.next_player_action()

    def tax(self):
        if self.is_turn_begin:
            # Before allowing the action to take effect, the opponent must not challenge it
            self.get_curr_action_player().last_action = TAX
            self.next_player_action()
        else:
            # PASS: Opponent did not challenge, so complete the action
            self.get_curr_action_player().add_coins(3)
            self.next_player_turn()

    def assassinate(self):
        curr_player = self.get_curr_action_player()
        curr_player.last_action = ASSASSINATE
        # Pay the coins whether or not the action is blocked/challenged
        curr_player.remove_coins(3)
        self.next_player_action()

    def exchange(self):
        if self.is_turn_begin:
            # Before drawing the 2 cards from the deck, the opponent must not challenge it
            self.get_curr_action_player().last_action = EXCHANGE
            self.next_player_action()
        else:
            # PASS: Opponent did not challenge, so draw 2 cards
            curr_player = self.get_curr_action_player()
            curr_player.add_card(self.draw_card())
            curr_player.add_card(self.draw_card())
            # Don't increment turn or action
            # It is still curr_player's choice of which cards to return to the deck

    def _exchange_return(self, lst):
        curr_player = self.get_curr_action_player()
        for ind in lst:
            self.deck.append(curr_player.cards.pop(ind))
        self.shuffle_deck()
        self.next_player_turn()

    def exchange_return_12(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_12
        self._exchange_return([0, 1])

    def exchange_return_13(self):
        curr_player = self.get_curr_action_player()
        curr_player.last_action = EXCHANGE_RETURN_13
        self._exchange_return([0, 2])
        # Card 2 has now moved to pos 1
        curr_player.is_card_face_up[0], curr_player.is_card_face_up[1] = curr_player.is_card_face_up[1], curr_player.is_card_face_up[0]

    def exchange_return_14(self):
        curr_player = self.get_curr_action_player()
        curr_player.last_action = EXCHANGE_RETURN_14
        self._exchange_return([0, 3])
        # Card 2 has now moved to pos 1
        curr_player.is_card_face_up[0], curr_player.is_card_face_up[1] = curr_player.is_card_face_up[1], curr_player.is_card_face_up[0]

    def exchange_return_23(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_23
        self._exchange_return([1, 2])

    def exchange_return_24(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_24
        self._exchange_return([1, 3])

    def exchange_return_34(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_34
        self._exchange_return([2, 3])

    def steal(self):
        if self.is_turn_begin:
            # Before allowing the action to take effect, the opponent must not block or challenge
            self.get_curr_action_player().last_action = STEAL
            self.next_player_action()
        else:
            # PASS: Opponent did not challenge, so complete the action
            curr_player = self.get_curr_action_player()
            opp_player = self.get_opp_player()

            num_steal = 2 if opp_player.coins >= 2 else 1

            opp_player.remove_coins(num_steal)
            curr_player.add_coins(num_steal)
            self.next_player_turn()

    def pass_(self):
        act = self.get_opp_player().last_action

        if act in [FOREIGN_AID, TAX, EXCHANGE, STEAL, BLOCK]:
            self.get_curr_action_player().last_action = PASS_
            self.next_player_action()
            getattr(self, self.actions[act])()

        else:
            print('Error: cannot pass after', CoupEnv.actions[act])
            return

    def block(self):
        ...

    def challenge(self):

        # Check if opp_player has the required card

        # If they do, curr_player loses a card

        # If they don't, opp_player loses a card

        act = self.get_opp_player().last_action

        if act in [TAX, ASSASSINATE, EXCHANGE, STEAL, BLOCK]:
            ...

        else:
            print('Error: cannot challenge', CoupEnv.actions[act])
            return

    def _lose_card(self, card):
        curr_player = self.get_curr_action_player()
        if curr_player.is_card_face_up[card]:
            print('Error: cannot lose a card that is already face up')
            return

        curr_player.is_card_face_up[card] = True
        curr_player.lost_challenge = False
        self.next_player_turn()

    def lose_card_1(self):
        self.get_curr_action_player().last_action = LOSE_CARD_1
        self._lose_card(0)

    def lose_card_2(self):
        self.get_curr_action_player().last_action = LOSE_CARD_2
        self._lose_card(1)



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
        13: 'pass_',       # only an option when asked whether you'd
                           # like to block or challenge your opponent's last move
        14: 'block',       # block the opponent's move
        15: 'challenge',   # challenge the opponent's move
        16: 'lose_card_1', # choose which card to lose
        17: 'lose_card_2'
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
