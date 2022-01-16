import gym
import numpy as np
from random import shuffle
import logging

logging.basicConfig()
logger = logging.getLogger('gym_coup')

# Cards
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

class Card:
    names = ['Assassin',
             'Ambassador',
             'Captain',
             'Contessa',
             'Duke']
    def __init__(self, val, is_face_up=False):
        self.val = val
        self.is_face_up = is_face_up

    def get_name(self):
        return Card.names[self.val]

    def __lt__(self, other):
        return (self.val < other.val or
                (self.val == other.val and self.is_face_up < other.is_face_up))

class Player:
    def __init__(self, id, is_human=False):
        self.id = id
        self.is_human = is_human
        self.cards = []
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

    def has_face_down_card(self, card_val):
        for i in range(2):
            c = self.cards[i]
            if c.val == card_val and not c.is_face_up:
                return True
        return False

    def get_obs(self):
        '''
        Return list of:
            Cards           Alph sorted hand for 1 player
            Is face up      If cards are face up or down
            # coins         (0 - 12)
            Last action
        '''
        c1 = self.cards[0]
        c2 = self.cards[1]
        return [c1.val,
                c2.val,
                c1.is_face_up,
                c2.is_face_up,
                self.coins,
                self.last_action]

    def _sort_cards(self):
        '''
        Always keep the cards sorted in alphabetical order.
        Since get_obs is run on each iter, decrease the amount of
        sorts we need by only sorting when cards are exchanged or lost.
        '''
        self.cards.sort()


class Game:
    '''
    2 player Coup game
    Can have any combination of human and cpu players
    '''
    def __init__(self, num_human_players=0):
        self.players = [Player(i, True) for i in range(num_human_players)]
        self.players += [Player(i+num_human_players, False) for i in range(2-num_human_players)]

        self.deck = [Card(i) for _ in range(3) for i in range(len(Card.names))]
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

        self.game_over = False

    def print_player(self, p_ind):
        p = self.players[p_ind]
        logger.info(f'P{p_ind + 1}: {p.cards[0].get_name()} | {p.cards[0].is_face_up} | ' + 
                                  f'{p.cards[1].get_name()} | {p.cards[1].is_face_up} | ' +
            f'{p.coins} | {"_" if p.last_action == None else CoupEnv.actions[p.last_action]}')

    def render(self):
        logger.info(f'Turn {self.turn_count}')
        logger.info('Player: Card1 | FaceUp | Card2 | FaceUp | Coins | LastAction')
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
        self.players[0]._sort_cards()
        self.players[1]._sort_cards()

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
            if not curr_player.cards[0].is_face_up:
                # Card is still in play. Can choose to give it up.
                valid += [LOSE_CARD_1]
            if not curr_player.cards[1].is_face_up:
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
                raise RuntimeError('Invalid action progression')

        elif curr_player.last_action == EXCHANGE:
            # It is curr_player's turn, and opp_player has approved the exchange

            if len(curr_player.cards) < 4:
                raise RuntimeError('Player mid-exchange should have 4 cards including any eliminated')
            
            valid = [EXCHANGE_RETURN_34]
            if not curr_player.cards[0].is_face_up:
                valid += [EXCHANGE_RETURN_13, EXCHANGE_RETURN_14]
            if not curr_player.cards[1].is_face_up:
                valid += [EXCHANGE_RETURN_23, EXCHANGE_RETURN_24]
            if (not curr_player.cards[0].is_face_up and
                not curr_player.cards[1].is_face_up):
                valid += [EXCHANGE_RETURN_12]

            return valid

        elif opp_player.last_action == BLOCK:
            # It is curr_player's turn and opp_player wants to block their move
            return [PASS_, CHALLENGE]
        
        else:
            raise RuntimeError('Invalid action progression')


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
            raise RuntimeError('Not possible to coup with < 7 coins')

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
            # CHALLENGE: curr_player had the ambassador, so complete the action
            curr_player = self.get_curr_action_player()
            curr_player.add_card(self.draw_card())
            curr_player.add_card(self.draw_card())
            curr_player._sort_cards()
            # Don't increment turn or action
            # It is still curr_player's choice of which cards to return to the deck

    def _exchange_return(self, lst):
        curr_player = self.get_curr_action_player()
        for ind in sorted(lst, reverse=True):
            self.deck.append(curr_player.cards.pop(ind))
        self.shuffle_deck()
        curr_player._sort_cards()

        if self.get_opp_player().lost_challenge:
            # opp still needs to choose a card to lose
            self.next_player_action()
        else:
            self.next_player_turn()

    def exchange_return_12(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_12
        self._exchange_return([0, 1])

    def exchange_return_13(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_13
        self._exchange_return([0, 2])

    def exchange_return_14(self):
        self.get_curr_action_player().last_action = EXCHANGE_RETURN_14
        self._exchange_return([0, 3])

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

        if act in [FOREIGN_AID, TAX, EXCHANGE, STEAL]:
            self.get_curr_action_player().last_action = PASS_
            self.next_player_action()
            # Complete the action
            getattr(self, CoupEnv.actions[act])()

        elif act == BLOCK:
            # Block succeeds, so nothing to do. Next turn.
            self.get_curr_action_player().last_action = PASS_
            self.next_player_turn()

        else:
            raise RuntimeError(f'Cannot pass after {CoupEnv.actions[act]}')

    def block(self):
        act = self.get_opp_player().last_action

        if act in [FOREIGN_AID, ASSASSINATE, STEAL]:
            self.get_curr_action_player().last_action = BLOCK
            self.next_player_action()
        else:
            raise RuntimeError(f'Cannot pass after {CoupEnv.actions[act]}')

    def challenge(self):
        curr_player = self.get_curr_action_player()
        opp_player = self.get_opp_player()
        # Check if opp_player has the required card
        # If they do, curr_player loses a card
        # If they don't, opp_player loses a card

        act = self.get_opp_player().last_action

        if act == TAX:
            curr_player.last_action = CHALLENGE

            if opp_player.has_face_down_card(DUKE):
                curr_player.lost_challenge = True
                # Replace the revealed card
                self._challenge_fail_replace_card(DUKE)
                
                # Complete the action
                opp_player.add_coins(3)
                
                # curr_player must lose a card
                # It is still their action
            else:
                opp_player.lost_challenge = True
                # opp_player must lose a card
                self.next_player_action()

        elif act == ASSASSINATE:
            curr_player.last_action = CHALLENGE

            if opp_player.has_face_down_card(ASSASSIN):
                # curr_player loses the game
                # Lose 1 card for assassination
                # and 1 card for losing challenge
                curr_player.cards[0].is_face_up = True
                curr_player.cards[1].is_face_up = True
                self.game_over = True
                logger.info('Game Over')
            else:
                opp_player.lost_challenge = True
                
                # Coins spent are returned in this one case
                opp_player.add_coins(3)
                
                # opp_player must lose a card
                self.next_player_action()

        elif act == EXCHANGE:
            curr_player.last_action = CHALLENGE

            if opp_player.has_face_down_card(AMBASSADOR):
                curr_player.lost_challenge = True
                # Replace the revealed card
                self._challenge_fail_replace_card(AMBASSADOR)

                # Complete the action
                self.next_player_action()
                self.exchange()

                # curr_player must lose a card
                # After _exchange_return is called it will switch to their action
            else:
                opp_player.lost_challenge = True
                # opp_player must lose a card
                self.next_player_action()

        elif act == STEAL:
            curr_player.last_action = CHALLENGE

            if opp_player.has_face_down_card(CAPTAIN):
                curr_player.lost_challenge = True
                # Replace the revealed card
                self._challenge_fail_replace_card(CAPTAIN)

                # Complete the action
                num_steal = 2 if curr_player.coins >= 2 else 1
                curr_player.remove_coins(num_steal)
                opp_player.add_coins(num_steal)
                # curr_player must lose a card
                # It is still their action
            else:
                opp_player.lost_challenge = True
                # opp_player must lose a card
                self.next_player_action()

        elif act == BLOCK:
            prev_act = curr_player.last_action
            curr_player.last_action = CHALLENGE

            if prev_act == FOREIGN_AID:
                if opp_player.has_face_down_card(DUKE):
                    curr_player.lost_challenge = True
                    # Replace the revealed card
                    self._challenge_fail_replace_card(DUKE)
                    # curr_player must lose a card
                    # It is still their action
                else:
                    opp_player.lost_challenge = True
                    
                    # Block failed, so complete the action
                    curr_player.add_coins(2)
                    
                    # opp_player must lose a card
                    self.next_player_action()

            elif prev_act == ASSASSINATE:
                if opp_player.has_face_down_card(CONTESSA):
                    curr_player.lost_challenge = True
                    # Replace the revealed card
                    self._challenge_fail_replace_card(CONTESSA)
                    # curr_player must lose a card
                    # It is still their action
                else:
                    # opp_player loses the game
                    # Lose 1 card for assassination
                    # and 1 card for losing challenge
                    opp_player.cards[0].is_face_up = True
                    opp_player.cards[1].is_face_up = True
                    self.game_over = True
                    logger.info('Game Over')

            elif prev_act == STEAL:
                if opp_player.has_face_down_card(CAPTAIN):
                    curr_player.lost_challenge = True
                    # Replace the revealed card
                    self._challenge_fail_replace_card(CAPTAIN)
                    # curr_player must lose a card
                    # It is still their action
                elif opp_player.has_face_down_card(AMBASSADOR):
                    curr_player.lost_challenge = True
                    # Replace the revealed card
                    self._challenge_fail_replace_card(AMBASSADOR)
                    # curr_player must lose a card
                    # It is still their action
                else:
                    opp_player.lost_challenge = True

                    # Block failed, so complete the action
                    num_steal = 2 if opp_player.coins >= 2 else 1
                    opp_player.remove_coins(num_steal)
                    curr_player.add_coins(num_steal)

                    # opp_player must lose a card
                    self.next_player_action()

            else:
                raise RuntimeError(f'Cannot block {CoupEnv.actions[prev_act]}')

        else:
            raise RuntimeError(f'Cannot challenge {CoupEnv.actions[act]}')

    def _challenge_fail_replace_card(self, card_val):
        # If the challenged player actually had the correct card,
        # shuffle it into the deck and give them a new card
        p = self.get_opp_player()
        for i in range(2):
            c = p.cards[i]
            if c.val == card_val and not c.is_face_up:
                self.deck.append(c)
                self.shuffle_deck()
                p.cards[i] = self.draw_card()
                p._sort_cards()
                return
        
        raise RuntimeError(f'Tried to replace card {Card.names[card_val]} that was not in player\'s hand')

    def _lose_card(self, card_ind):
        curr_player = self.get_curr_action_player()
        if curr_player.cards[card_ind].is_face_up:
            raise RuntimeError(f'Cannot lose a card that is already face up')

        curr_player.cards[card_ind].is_face_up = True
        curr_player.lost_challenge = False
        curr_player._sort_cards()

        # Check if the player has no cards remaining
        self.game_over = not (False in [x.is_face_up for x in curr_player.cards])

        if self.game_over:
            logger.info('Game Over')

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
        self.game = None

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
        if isinstance(action, int):
            action = self.actions[action]
        elif isinstance(action, str):
            pass
        else:
            raise RuntimeError(f'Cannot step with action type {type(action)}')

        getattr(self.game, action)()

        # TODO return obs, reward, done, info
        return (list(), 0, self.game.game_over, dict())
    
    def reset(self):
        self.game = Game(self.num_human_players)

    def render(self, mode='human'):
        if self.game is not None:
            self.game.render()

    def get_valid_actions(self, text=False):
        '''
        Get the valid actions, in either number or text form
        '''
        if self.game is None:
            return None

        a = self.game.get_valid_actions()
        logger.debug(f'Valid actions: {[self.actions[x] for x in a]}')
        if text:
            return [self.actions[x] for x in a]
        else:
            return a

    def get_obs(self):
        # TODO
        pass
